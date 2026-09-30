"""Local regression checks for the isolated Telmisartan NORA/VCC case.

The numeric values below are synthetic UI fixtures, not experimental results or
proposed regulatory acceptance criteria. Run from any working directory:
    python3 work/vcc/scripts/validate_telmisartan.py
"""
from __future__ import annotations

import copy
import importlib.util
import math
from pathlib import Path
import sys
import traceback
from unittest.mock import patch

import pandas as pd
from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
APP = ROOT / "streamlit_app.py"


def clean_run(page: AppTest) -> AppTest:
    page.run(timeout=30)
    assert not page.exception, [(e.message, e.stack_trace) for e in page.exception]
    return page


def start(page_name="case", strategy="triple") -> AppTest:
    page = AppTest.from_file(str(APP))
    page.query_params.update({"enter": "1", "page": page_name, "case": "telmisartan",
                              "strategy": strategy, "lang": "ko"})
    return clean_run(page)


def rendered_frame(page: AppTest, column: str) -> pd.DataFrame:
    frames = [element.value for element in page.dataframe if column in element.value.columns]
    assert len(frames) == 1, f"Expected one rendered table containing {column!r}, found {len(frames)}"
    return frames[0]


def edit_rows(page: AppTest, key: str, rows: dict) -> None:
    # Streamlit AppTest has no data_editor.set_value API; inject the documented
    # frontend edit delta, then run the actual editor and state-save path.
    assert key in page.session_state, f"Editor was not rendered: {key}"
    page.session_state[key] = {"edited_rows": rows, "added_rows": [], "deleted_rows": []}
    clean_run(page)


def assert_initial_state_and_calculation_reuse() -> None:
    page = start()
    assert page.session_state["active_page"] == "case"
    assert page.selectbox(key="tel_vcc_strategy").value == "triple"
    reviews = page.session_state["tel_vcc_reviews_triple"]
    assert len(reviews) > 0
    assert set(reviews["status"]) == {"미확인"}, "Case reviews must start unverified"
    assert (reviews[["evidence", "action"]] == "").all().all(), "No fabricated evidence/actions"
    rules = page.session_state["tel_vcc_rules_triple"]
    assert rules["Result"].isna().all(), "Actual trial/assay results must start blank"
    assert set(rendered_frame(page, "Review state")["Review state"]) == {"Info"}

    import app
    with patch.object(app, "calculate_sample_prep", wraps=app.calculate_sample_prep) as reused:
        clean_run(page)
        assert reused.call_count == 3, "Each component must reuse the existing preparation calculator"
    expected = {"Telmisartan": 40.0, "Amlodipine": 5.0, "Indapamide": 2.5}
    table = rendered_frame(page, "Preparation check").set_index("Component")
    assert set(table.index) == set(expected)
    for component, concentration in expected.items():
        assert math.isclose(table.loc[component, "Actual ug/mL"], concentration)
        assert math.isclose(table.loc[component, "Target ug/mL"], concentration)
        assert math.isclose(table.loc[component, "Difference %"], 0.0, abs_tol=1e-10)
        assert table.loc[component, "Preparation check"] == "Pass"


def assert_consecutive_edits_recalculate() -> None:
    page = start()
    edit_rows(page, "tel_vcc_review_editor_triple_ko", {
        0: {"status": "보완 필요", "evidence": "Synthetic source v7", "action": "Obtain supplier confirmation"}})
    edit_rows(page, "tel_vcc_prep_editor_triple", {0: {"Weighed mg": 45.0}})
    prep = rendered_frame(page, "Preparation check").set_index("Component")
    assert prep.loc["Telmisartan", "Actual ug/mL"] == 45.0
    assert prep.loc["Telmisartan", "Target ug/mL"] == 40.0
    assert prep.loc["Telmisartan", "Difference %"] == 12.5
    assert prep.loc["Telmisartan", "Preparation check"] == "Hold"
    assert prep.loc["Amlodipine", "Preparation check"] == "Pass"

    edit_rows(page, "tel_vcc_rule_editor_triple", {0: {"Result": 105.0}})
    result = rendered_frame(page, "Review state").set_index("Component")
    assert result.loc["Telmisartan", "Review state"] == "Review"
    assert result.loc["Amlodipine", "Review state"] == "Info"
    edit_rows(page, "tel_vcc_rule_editor_triple", {0: {"Result": 105.0, "Upper": 110.0}})
    assert rendered_frame(page, "Review state").iloc[0]["Review state"] == "Pass"


def assert_case_navigation_persistence() -> None:
    page = start()
    edit_rows(page, "tel_vcc_review_editor_triple_ko", {
        0: {"status": "보완 필요", "evidence": "Synthetic source v7", "action": "Obtain supplier confirmation"}})
    edit_rows(page, "tel_vcc_prep_editor_triple", {0: {"Weighed mg": 45.0}})
    edit_rows(page, "tel_vcc_rule_editor_triple", {0: {"Result": 105.0, "Upper": 110.0}})
    saved = {key: page.session_state[key].copy(deep=True) for key in (
        "tel_vcc_reviews_triple", "tel_vcc_prep_triple", "tel_vcc_rules_triple")}

    def assert_saved():
        assert not page.exception
        for key, frame in saved.items():
            pd.testing.assert_frame_equal(page.session_state[key], frame, obj=key)

    for strategy in ("generic", "dual", "triple"):
        page.selectbox(key="tel_vcc_strategy").set_value(strategy)
        clean_run(page)
        assert_saved()
        expected_count = {"generic": 1, "dual": 2, "triple": 3}[strategy]
        assert len(rendered_frame(page, "Preparation check")) == expected_count
        if strategy != "triple":
            assert page.session_state[f"tel_vcc_rules_{strategy}"]["Result"].isna().all()

    for lang in ("en", "ko"):
        page.radio(key="language_choice").set_value(lang)
        clean_run(page)
        assert page.session_state["lang"] == lang
        assert page.selectbox(key="tel_vcc_strategy").value == "triple", "Language changed the chosen strategy"
        assert_saved()

    for destination in ("intake", "validation", "case"):
        page.selectbox(key="detail_page_widget").set_value(destination)
        clean_run(page)
        assert page.session_state["active_page"] == destination
        assert_saved()
    assert page.selectbox(key="tel_vcc_strategy").value == "triple"
    assert rendered_frame(page, "Preparation check").iloc[0]["Preparation check"] == "Hold"
    assert rendered_frame(page, "Review state").iloc[0]["Review state"] == "Pass"


def assert_existing_workbench_isolation() -> None:
    page = start(page_name="intake")
    import app
    assert page.session_state["profile_values"]["active_substance"] == "Naltrexone"
    product = "Naltrexone PLGA retained-project fixture"
    page.text_input(key="profile_product").set_value(product)
    clean_run(page)
    edit_rows(page, "intake_editor", {0: {
        app.COLUMN_KO["Client question"]: "Synthetic existing Naltrexone review question"}})
    profile = copy.deepcopy(page.session_state["profile_values"])
    table_names = ["intake_df", "evidence_df", "spec_df", "dmf_df", "dmf_source_df", "ctd_document_df", "validation_df"]
    saved = {key: page.session_state[key].copy(deep=True) for key in table_names}

    page.selectbox(key="detail_page_widget").set_value("case")
    clean_run(page)
    page.selectbox(key="tel_vcc_strategy").set_value("triple")
    clean_run(page)
    edit_rows(page, "tel_vcc_rule_editor_triple", {0: {"Result": 105.0}})
    for lang in ("en", "ko"):
        page.radio(key="language_choice").set_value(lang)
        clean_run(page)
    assert page.session_state["profile_values"] == profile
    for key, frame in saved.items():
        pd.testing.assert_frame_equal(page.session_state[key], frame, obj=f"Unrelated workbench {key}")

    page.selectbox(key="detail_page_widget").set_value("intake")
    clean_run(page)
    assert page.text_input(key="profile_product").value == product
    assert page.session_state["profile_values"] == profile
    for key, frame in saved.items():
        pd.testing.assert_frame_equal(page.session_state[key], frame, obj=f"Returned workbench {key}")


def assert_handoff_validation_and_shared_model() -> None:
    import telmisartan_case as vcc
    nora_path = ROOT.parent / "nora" / "telmisartan_case.py"
    # The standalone VCC repository does not include a sibling NORA checkout.
    # Always test its canonical packet validation; cross-check NORA when present.
    nora = None
    if nora_path.is_file():
        spec = importlib.util.spec_from_file_location("nora_telmisartan_validation_fixture", nora_path)
        assert spec is not None and spec.loader is not None
        nora = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(nora)

    case = vcc.load_case()
    for strategy in case["strategies"]:
        values = copy.deepcopy(strategy["assumptions"])
        values["eligible_patients"] *= 0.5
        values["launch_year"] += 1
        expected = vcc.build_handoff(strategy["id"], values)
        incoming = (nora.build_handoff(strategy["id"], values)
                    if nora is not None else copy.deepcopy(expected))
        incoming["summary"] = {"peak_risk_adjusted_krw_m": 999_999_999_999}
        assert vcc.validate_handoff(incoming) == expected, "VCC must recalculate imported assumptions"
        if nora is not None:
            assert nora.validate_handoff(expected) == expected, "Two copies of the shared model disagree"

    valid = vcc.build_handoff("triple", next(s for s in case["strategies"] if s["id"] == "triple")["assumptions"])
    invalid_packets = []
    for field, value in (("schema_version", 2), ("case_id", "other"), ("market", "US"),
                         ("currency", "USD"), ("evidence_type", "reported_sales"),
                         ("anchor_year", 1999), ("horizon", 99), ("strategy_id", "unknown")):
        payload = copy.deepcopy(valid)
        payload[field] = value
        invalid_packets.append((field, payload))
    for field, value in (("eligible_patients", -1), ("eligible_patients", True),
                         ("success_pct", float("nan")), ("annual_net_price_krw", float("inf")),
                         ("launch_year", 2028.5), ("initial_share_pct", 101)):
        payload = copy.deepcopy(valid)
        payload["assumptions"][field] = value
        invalid_packets.append((field, payload))
    missing = copy.deepcopy(valid)
    missing["assumptions"].pop("launch_year")
    invalid_packets.append(("missing assumption", missing))
    extra = copy.deepcopy(valid)
    extra["assumptions"]["reported_product_sales"] = 123
    invalid_packets.append(("unknown assumption", extra))
    for label, payload in invalid_packets:
        try:
            vcc.validate_handoff(payload)
        except (ValueError, TypeError):
            pass
        else:
            raise AssertionError(f"Invalid {label} was accepted")


def main() -> int:
    tests = [assert_initial_state_and_calculation_reuse, assert_consecutive_edits_recalculate,
             assert_case_navigation_persistence,
             assert_existing_workbench_isolation, assert_handoff_validation_and_shared_model]
    failures = []
    for test in tests:
        try:
            test()
        except Exception:
            failures.append(test.__name__)
            print(f"FAIL {test.__name__}")
            traceback.print_exc()
        else:
            print(f"PASS {test.__name__}")
    print(f"Telmisartan validation: {len(tests)-len(failures)}/{len(tests)} groups passed")
    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(main())

"""Check dilution units, correction provenance, and review confirmation behavior."""
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from streamlit.testing.v1 import AppTest
from validation_extension import (
    PROFILES,
    calculate_preparation_basis,
    calculation_basis_report_frame,
    calculation_evidence_status,
    effective_correction_pct,
    invalidate_calculation_context,
)


def close(actual: float, expected: float) -> None:
    assert abs(actual - expected) <= max(1e-9, abs(expected) * 1e-9), (actual, expected)


def baseline(**overrides: object) -> dict:
    values = dict(reference_conc=2.5, level_pct=100, weighed_mg=25, purity_pct=99.8,
                  stock_volume_ml=100, aliquot_ml=1, final_volume_ml=50, dilution_factor=2)
    values.update(overrides)
    return calculate_preparation_basis(**values)


def validate_corrections_and_units() -> None:
    default = baseline()
    close(default["stock_conc"], 249.5)
    close(default["final_conc"], 2.495)
    close(default["diff_pct"], -0.2)
    assert default["gate"] == "Pass"
    combined = baseline(moisture_pct=2)
    close(combined["final_conc"], 2.495)
    assert combined["moisture_pct"] is None
    separate = baseline(correction_mode="dry_purity_and_moisture", moisture_pct=2)
    close(separate["effective_correction_pct"], 97.804)
    close(separate["final_conc"], 2.4451)
    assert separate["gate"] == "Review"
    close(baseline(dilution_factor=4)["final_conc"], 1.2475)
    for unit, reference, final in (("ng/mL", 2500, 2495), ("mg/mL", 0.0025, 0.002495), ("μg/mL", 2.5, 2.495)):
        result = baseline(reference_conc=reference, unit=unit)
        close(result["final_conc"], final)
        close(result["diff_pct"], -0.2)
        assert result["gate"] == "Pass"
    for unit in ("ug/g", "ppm", "ug/g or ppm", "", "wrong unit"):
        result = baseline(unit=unit)
        assert result["gate"] == "Info" and result["diff_pct"] is None
        assert result["output_unit"] == "ug/mL" and not result["unit_comparable"]
        close(result["final_conc"], 2.495)
    nitrosamine = next(item for item in PROFILES if item["key"] == "nitrosamines")["prep"]
    ref, unit, level, mass, purity, stock, aliquot, final, dilution = nitrosamine
    result = calculate_preparation_basis(ref, level, mass, purity, stock, aliquot, final, dilution, unit)
    close(result["final_conc"], 30.0000030000003)
    assert result["gate"] == "Hold", "A ug/mL result must not be mislabeled as a passing ng/mL example"
    for changes in ({"stock_volume_ml": 0}, {"dilution_factor": 0}, {"weighed_mg": -1}, {"reference_conc": float("nan")},
                    {"correction_mode": "dry_purity_and_moisture", "purity_pct": 101},
                    {"correction_mode": "dry_purity_and_moisture", "moisture_pct": 101}):
        try:
            baseline(**changes)
        except ValueError:
            pass
        else:
            raise AssertionError(f"Invalid preparation input accepted: {changes}")
    close(effective_correction_pct(100, 100, "dry_purity_and_moisture"), 0)
    print("PASS: dimensional formulas, dilution, correction modes, and invalid inputs")


def validate_evidence_state() -> None:
    record = baseline()
    assert calculation_evidence_status(record)[0] == "Unconfirmed"
    record.update({field: "Fixture evidence" for field in (
        "source_document", "source_version", "source_location", "application_scope",
        "reference_basis", "correction_basis", "recovery_basis",
    )})
    record.update(confirmation_requested="Reviewer confirmed", correlation_basis="Reported r; R² evidence needed")
    assert calculation_evidence_status(record)[0] == "Unconfirmed"
    record["correlation_basis"] = "Reported R²"
    assert calculation_evidence_status(record) == ("Reviewer confirmation recorded", [])
    record.update(evidence_status="Reviewer confirmation recorded", profile_context={"product": "Product A", "batch": "A-001"})
    changed = invalidate_calculation_context(record, {"product": "Product B", "batch": "B-001"})
    assert changed["evidence_status"] == "Unconfirmed"
    assert changed["prior_profile_context"] == {"product": "Product A", "batch": "A-001"}
    assert changed["source_version"] == record["source_version"]
    assert record["evidence_status"] == "Reviewer confirmation recorded", "Prior evidence record was overwritten"
    record["unit_comparable"] = False
    assert "unit_conversion_basis" in calculation_evidence_status(record)[1]
    print("PASS: sources, applicability, and r/R² cannot auto-confirm missing evidence")


def no_exception(page: AppTest) -> None:
    assert not page.exception, page.exception


def run(page: AppTest) -> AppTest:
    page.run(timeout=30)
    no_exception(page)
    return page


def validate_ui_and_memo() -> None:
    page = AppTest.from_file(str(ROOT / "streamlit_app.py"))
    page.query_params.update({"enter": "1", "page": "validation", "lang": "en"})
    run(page)
    prefix = "ext_prep_assay"
    assert page.number_input(key=f"{prefix}_weighed").value == 25.0
    assert page.number_input(key=f"{prefix}_moisture").disabled
    assert page.session_state["last_calc"]["evidence_status"] == "Unconfirmed"
    assert "[ug/mL]" in page.session_state["last_calc"]["formula"]
    page.selectbox(key=f"{prefix}_correction_mode").set_value("dry_purity_and_moisture")
    run(page)
    page.number_input(key=f"{prefix}_moisture").set_value(2.0)
    run(page)
    close(page.session_state["last_calc"]["final_conc"], 2.4451)
    page.selectbox(key=f"{prefix}_correction_mode").set_value("combined")
    run(page)
    close(page.session_state["last_calc"]["final_conc"], 2.495)
    assert page.number_input(key=f"{prefix}_moisture").value == 2.0
    assert page.number_input(key=f"{prefix}_moisture").disabled
    page.selectbox(key=f"{prefix}_confirmation_requested").set_value("Reviewer confirmed")
    run(page)
    assert page.session_state["last_calc"]["evidence_status"] == "Unconfirmed"
    fields = {
        "source_document": "CoA fixture / analytical method",
        "source_version": "Version 7 / effective 2026-09-01",
        "source_location": "Page 3 / table 2 / cell D5",
        "application_scope": "Fixture product / batch B-007 / assay method 7",
        "reference_basis": "Label claim target 2.5 ug/mL, method page 3",
        "correction_basis": "As-is potency 99.8%; moisture included",
        "recovery_basis": "(spiked measured − unspiked measured) / added × 100",
    }
    for field, value in fields.items():
        page.text_input(key=f"{prefix}_{field}").set_value(value)
    page.selectbox(key=f"{prefix}_correlation_basis").set_value("Reported R²")
    run(page)
    assert page.session_state["last_calc"]["evidence_status"] == "Unconfirmed", "Evidence edits require a fresh confirmation"
    page.selectbox(key=f"{prefix}_confirmation_requested").set_value("Unconfirmed")
    run(page)
    page.selectbox(key=f"{prefix}_confirmation_requested").set_value("Reviewer confirmed")
    run(page)
    assert page.session_state["last_calc"]["evidence_status"] == "Reviewer confirmation recorded"
    original_context = dict(page.session_state["last_calc"]["profile_context"])
    page.selectbox(key="detail_page_widget").set_value("response")
    run(page)
    assert page.session_state["last_calc"]["evidence_status"] == "Reviewer confirmation recorded"
    page.text_input(key="profile_product").set_value("Different applicable product fixture")
    run(page)
    changed_record = page.session_state["calculation_basis_records"]["assay"]
    assert changed_record["evidence_status"] == "Unconfirmed"
    assert page.session_state["last_calc"]["evidence_status"] == "Unconfirmed"
    assert changed_record["profile_context"] == original_context
    assert changed_record["current_profile_context"]["product"] == "Different applicable product fixture"
    packet_after_product = "\n".join(str(item.value) for item in page.text_area)
    for fragment in ("Confirm applicability after product / batch / profile change", "Prior product profile", original_context["product"], fields["source_document"]):
        assert fragment in packet_after_product, fragment
    page.selectbox(key="detail_page_widget").set_value("validation")
    run(page)
    assert page.session_state["last_calc"]["evidence_status"] == "Unconfirmed"
    page.selectbox(key=f"{prefix}_confirmation_requested").set_value("Unconfirmed")
    run(page)
    page.selectbox(key=f"{prefix}_confirmation_requested").set_value("Reviewer confirmed")
    run(page)
    assert page.session_state["last_calc"]["evidence_status"] == "Reviewer confirmation recorded"
    page.selectbox(key="detail_page_widget").set_value("response")
    run(page)
    page.text_input(key="profile_batch").set_value("Changed-batch-B-008")
    run(page)
    assert page.session_state["calculation_basis_records"]["assay"]["evidence_status"] == "Unconfirmed"
    assert page.session_state["last_calc"]["evidence_status"] == "Unconfirmed"
    packet_after_batch = "\n".join(str(item.value) for item in page.text_area)
    assert "Changed-batch-B-008" in packet_after_batch
    assert "Confirm applicability after product / batch / profile change" in packet_after_batch
    page.selectbox(key="detail_page_widget").set_value("validation")
    run(page)
    page.selectbox(key=f"{prefix}_confirmation_requested").set_value("Unconfirmed")
    run(page)
    page.selectbox(key=f"{prefix}_confirmation_requested").set_value("Reviewer confirmed")
    run(page)
    assert page.session_state["last_calc"]["evidence_status"] == "Reviewer confirmation recorded"
    page.number_input(key=f"{prefix}_weighed").set_value(30.0)
    run(page)
    assert page.session_state["last_calc"]["evidence_status"] == "Unconfirmed"
    assert "reviewer_reconfirmation_after_input_change" in page.session_state["last_calc"]["missing_evidence"]
    records = page.session_state["calculation_basis_records"]
    report = calculation_basis_report_frame(records)
    assert fields["source_location"] in report["Value"].tolist()
    page.selectbox(key="detail_page_widget").set_value("response")
    run(page)
    packet = "\n".join(str(item.value) for item in page.text_area)
    for fragment in ("Calculation Sources and Preparation Basis", "Page 3 / table 2 / cell D5", "Version 7", "Unconfirmed", "Recovery calculation basis", "Dilution steps", "Reported R²", "mass [mg]"):
        assert fragment in packet, fragment
    page.selectbox(key="detail_page_widget").set_value("validation")
    run(page)
    assert page.text_input(key=f"{prefix}_source_version").value == fields["source_version"]
    assert page.number_input(key=f"{prefix}_weighed").value == 30.0
    page.radio(key="language_choice").set_value("ko")
    run(page)
    assert page.text_input(key=f"{prefix}_source_document").value == fields["source_document"]
    page.button(key="vcc_ext_elemental_impurities").click()
    run(page)
    assert page.session_state["last_calc"]["gate"] == "Info"
    assert page.session_state["last_calc"]["diff_pct"] is None
    assert page.session_state["last_calc"]["output_unit"] == "ug/mL"
    page.button(key="vcc_ext_nitrosamines").click()
    run(page)
    assert page.session_state["last_calc"]["gate"] == "Hold"
    assert page.session_state["last_calc"]["unit"] == "ng/mL"
    print("PASS: Streamlit controls, numeric/profile confirmation invalidation, persistence, memo export, and unit-safe examples")


if __name__ == "__main__":
    validate_corrections_and_units()
    validate_evidence_state()
    validate_ui_and_memo()
    print("Calculation basis validation passed")

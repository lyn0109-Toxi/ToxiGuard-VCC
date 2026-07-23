from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import (
    calculate_sample_prep,
    default_validation_item_tables,
    evaluate_lod_linearity,
    evaluate_rule,
    format_report_diff,
    format_report_number,
)
from validation_extension import (
    ELEMENTAL_IMPURITY_ELEMENTS,
    apply_q3d_pde_limits,
    elemental_scope_frame,
    evaluate_q14_problem,
    pde_concentration_limits,
    q3b_threshold_frame,
    q14_problem_frame,
)


def approx(actual: float, expected: float, tolerance: float = 1e-6) -> None:
    if abs(actual - expected) > tolerance:
        raise AssertionError(f"Expected {expected}, got {actual}")


def assert_contains(values: list[str], expected: str) -> None:
    if not any(expected in value for value in values):
        raise AssertionError(f"Expected note containing {expected!r}, got {values}")


def validate_sample_preparation() -> None:
    baseline = calculate_sample_prep(
        reference_conc=2.5,
        level_pct=100,
        weighed_mg=25,
        purity_pct=99.8,
        stock_volume_ml=100,
        aliquot_ml=1,
        final_volume_ml=50,
        dilution_factor=2,
    )
    approx(float(baseline["stock_conc"]), 249.5)
    approx(float(baseline["final_conc"]), 2.495)
    approx(float(baseline["target_conc"]), 2.5)
    approx(float(baseline["diff_pct"]), -0.2)
    assert baseline["gate"] == "Pass"

    high_dilution = calculate_sample_prep(
        reference_conc=2.5,
        level_pct=100,
        weighed_mg=25,
        purity_pct=99.8,
        stock_volume_ml=100,
        aliquot_ml=1,
        final_volume_ml=50,
        dilution_factor=10,
    )
    approx(float(high_dilution["final_conc"]), 0.499)
    approx(float(high_dilution["diff_pct"]), -80.04)
    assert high_dilution["gate"] == "Hold"

    review_edge = calculate_sample_prep(
        reference_conc=2.5,
        level_pct=100,
        weighed_mg=23.8,
        purity_pct=100,
        stock_volume_ml=100,
        aliquot_ml=1,
        final_volume_ml=50,
        dilution_factor=2,
    )
    approx(float(review_edge["final_conc"]), 2.38)
    approx(float(review_edge["diff_pct"]), -4.8)
    assert review_edge["gate"] == "Review"

    half_aliquot = calculate_sample_prep(
        reference_conc=2.5,
        level_pct=100,
        weighed_mg=25,
        purity_pct=99.8,
        stock_volume_ml=100,
        aliquot_ml=0.5,
        final_volume_ml=50,
        dilution_factor=2,
    )
    approx(float(half_aliquot["final_conc"]), 1.2475)
    approx(float(half_aliquot["diff_pct"]), -50.1)
    assert half_aliquot["gate"] == "Hold"

    zero_target_with_analyte = calculate_sample_prep(
        reference_conc=2.5,
        level_pct=0,
        weighed_mg=25,
        purity_pct=99.8,
        stock_volume_ml=100,
        aliquot_ml=1,
        final_volume_ml=50,
        dilution_factor=2,
    )
    assert zero_target_with_analyte["diff_pct"] is None
    assert zero_target_with_analyte["gate"] == "Hold"

    true_blank = calculate_sample_prep(
        reference_conc=2.5,
        level_pct=0,
        weighed_mg=0,
        purity_pct=99.8,
        stock_volume_ml=100,
        aliquot_ml=0,
        final_volume_ml=50,
        dilution_factor=2,
    )
    approx(float(true_blank["final_conc"]), 0.0)
    approx(float(true_blank["diff_pct"]), 0.0)
    assert true_blank["gate"] == "Pass"


def validate_lod_linearity() -> None:
    default = evaluate_lod_linearity(
        reference_conc=2.5,
        lod=0.05,
        loq=0.15,
        r2=0.9992,
        intercept=240,
        response_100=31125,
        response_loq=1867.5,
        lowest_level_pct=20,
    )
    approx(float(default["lod_pct"]), 2.0)
    approx(float(default["loq_pct"]), 6.0)
    approx(float(default["intercept_100_pct"]), 0.7710843373493976)
    approx(float(default["intercept_loq_pct"]), 12.85140562248996)
    assert_contains(default["notes"], "LOQ response")

    low_r2 = evaluate_lod_linearity(1, 0.01, 0.05, 0.985, 1, 1000, 500, 10)
    assert_contains(low_r2["notes"], "R2 is below 0.99")

    high_intercept = evaluate_lod_linearity(1, 0.01, 0.05, 0.999, 1000, 30000, 5000, 10)
    assert_contains(high_intercept["notes"], "2% of the 100% response")
    assert_contains(high_intercept["notes"], "5% of the LOQ response")

    loq_above_range = evaluate_lod_linearity(1, 0.01, 0.25, 0.999, 1, 30000, 5000, 20)
    assert_contains(loq_above_range["notes"], "LOQ is higher than the lowest linearity level")

    acceptable = evaluate_lod_linearity(1, 0.01, 0.05, 0.999, 10, 30000, 10000, 10)
    assert acceptable["notes"] == ["LOD/LOQ and intercept risk are acceptable for the current reference concentration."]


def validate_result_gates() -> None:
    cases = [
        ({"Result": 100, "Rule": "between", "Lower": 95, "Upper": 105}, "Pass"),
        ({"Result": 94.99, "Rule": "between", "Lower": 95, "Upper": 105}, "Review"),
        ({"Result": 105.01, "Rule": "between", "Lower": 95, "Upper": 105}, "Review"),
        ({"Result": 0.9901, "Rule": "gte", "Lower": 0.99, "Upper": None}, "Pass"),
        ({"Result": 0.9899, "Rule": "gte", "Lower": 0.99, "Upper": None}, "Review"),
        ({"Result": 1.99, "Rule": "lte", "Lower": None, "Upper": 2.0}, "Pass"),
        ({"Result": 2.01, "Rule": "lte", "Lower": None, "Upper": 2.0}, "Review"),
        ({"Result": None, "Rule": "between", "Lower": 95, "Upper": 105}, "Info"),
        ({"Result": 123, "Rule": "info", "Lower": None, "Upper": None}, "Info"),
    ]
    for row, expected in cases:
        actual = evaluate_rule(pd.Series(row))
        if actual != expected:
            raise AssertionError(f"Expected {expected}, got {actual} for {row}")


def validate_test_specific_validation_tables() -> None:
    tables = default_validation_item_tables()
    expected_keys = {"assay", "related_substances", "dissolution", "elemental_impurities", "nitrosamines"}
    if set(tables) != expected_keys:
        raise AssertionError(f"Unexpected validation item keys: {set(tables)}")
    for key, table in tables.items():
        required_columns = {"Item", "Result", "Unit", "Rule", "Lower", "Upper", "Note"}
        missing = required_columns.difference(table.columns)
        if missing:
            raise AssertionError(f"{key} table is missing columns: {missing}")
        if len(table) < 5:
            raise AssertionError(f"{key} table should contain enough test-specific review rows")

    nitrosamines = tables["nitrosamines"]
    if not any(nitrosamines["Item"].astype(str).str.contains("acceptable intake")):
        raise AssertionError("Nitrosamine table should connect LOQ to acceptable intake")

    metals = tables["elemental_impurities"]
    if not any(metals["Item"].astype(str).str.contains("control threshold")):
        raise AssertionError("Elemental impurity table should connect LOQ to control threshold")


def validate_q3d_elemental_scope() -> None:
    if len(ELEMENTAL_IMPURITY_ELEMENTS) != 24:
        raise AssertionError(f"Expected 24 Q3D elements, got {len(ELEMENTAL_IMPURITY_ELEMENTS)}")
    elements = {row["Element"] for row in ELEMENTAL_IMPURITY_ELEMENTS}
    expected = {
        "As", "Cd", "Hg", "Pb", "Co", "Ni", "V",
        "Ag", "Au", "Ir", "Os", "Pd", "Pt", "Rh", "Ru", "Se", "Tl",
        "Ba", "Cr", "Cu", "Li", "Mo", "Sb", "Sn",
    }
    if elements != expected:
        raise AssertionError(f"Unexpected Q3D element set: {sorted(elements)}")

    core = elemental_scope_frame("core7")
    core_included = set(core[core["Include"]]["Element"])
    if core_included != {"As", "Cd", "Hg", "Pb", "Co", "Ni", "V"}:
        raise AssertionError(f"Unexpected Core 7 elements: {sorted(core_included)}")

    full = elemental_scope_frame("full24")
    if int(full["Include"].sum()) != 24:
        raise AssertionError("Full Q3D 24 mode should include all 24 elements")

    oral_core = apply_q3d_pde_limits(elemental_scope_frame("core7", "Oral"), 2.5)
    as_row = oral_core[oral_core["Element"] == "As"].iloc[0]
    approx(float(as_row["Route PDE entered (ug/day)"]), 15.0)
    approx(float(as_row["Permitted concentration (ug/g)"]), 6.0)
    approx(float(as_row["Control threshold concentration (ug/g)"]), 1.8)
    approx(float(as_row["Calculated LOQ vs control threshold (ug/g)"]), 0.18)

    parenteral_core = elemental_scope_frame("core7", "Parenteral")
    cd_row = parenteral_core[parenteral_core["Element"] == "Cd"].iloc[0]
    approx(float(cd_row["Route PDE entered (ug/day)"]), 2.0)


def validate_pde_limit_calculations() -> None:
    limits = pde_concentration_limits(15.0, 2.5)
    approx(float(limits["permitted_conc_ug_g"]), 6.0)
    approx(float(limits["control_threshold_ug_day"]), 4.5)
    approx(float(limits["control_threshold_conc_ug_g"]), 1.8)

    q3b = q3b_threshold_frame(mdd_mg_day=50.0, impurity_pde_ug_day=200.0, sample_conc_mg_ml=0.5)
    qualification = q3b[q3b["Threshold"] == "Qualification"].iloc[0]
    target = q3b[q3b["Threshold"] == "Validation target"].iloc[0]
    approx(float(qualification["Limit (%)"]), 0.4)
    approx(float(target["Limit (%)"]), 0.4)
    approx(float(target["Method concentration (ug/mL)"]), 2.0)

    high_mdd = q3b_threshold_frame(mdd_mg_day=1900.0, impurity_pde_ug_day=1000.0, sample_conc_mg_ml=1.0)
    target_high_mdd = high_mdd[high_mdd["Threshold"] == "Validation target"].iloc[0]
    approx(float(target_high_mdd["Limit (%)"]), 1000.0 / (1900.0 * 10.0))
    approx(float(target_high_mdd["Method concentration (ug/mL)"]), 1000.0 * (1000.0 / (1900.0 * 10.0)) / 100.0)


def validate_q14_method_setup_check() -> None:
    frame = q14_problem_frame("Assay / 함량")
    required_columns = {
        "Test item",
        "Q14 check",
        "Status",
        "Risk",
        "Problem signal",
        "Evidence to request",
        "CTD update",
        "Q14 anchor",
    }
    missing = required_columns.difference(frame.columns)
    if missing:
        raise AssertionError(f"Q14 problem frame is missing columns: {missing}")
    if len(frame) < 8:
        raise AssertionError("Q14 problem frame should contain the core analytical procedure development checks")
    joined = " | ".join(frame["Q14 check"].astype(str))
    for expected in ["ATP", "Robustness", "control strategy", "lifecycle"]:
        if expected.lower() not in joined.lower():
            raise AssertionError(f"Q14 problem frame should include {expected!r}")

    gated = frame.copy()
    gated["Gate"] = gated.apply(evaluate_q14_problem, axis=1)
    if int((gated["Gate"] == "Review").sum()) < 1:
        raise AssertionError("Default Q14 frame should surface method setup review items")
    if evaluate_q14_problem(pd.Series({"Status": "Defined", "Risk": "High"})) != "Pass":
        raise AssertionError("Defined Q14 item should pass even when the inherent topic risk is high")
    if evaluate_q14_problem(pd.Series({"Status": "Gap", "Risk": "Low"})) != "Review":
        raise AssertionError("Gap status should trigger Q14 review")


def validate_report_formatting() -> None:
    assert format_report_number(None) == "N/A"
    assert format_report_number("Not run") == "Not run"
    assert format_report_number(2.495) == "2.4950"
    assert format_report_diff(None) == "N/A"
    assert format_report_diff("Not run") == "Not run"
    assert format_report_diff(-0.2) == "-0.20%"


def main() -> None:
    validate_sample_preparation()
    validate_lod_linearity()
    validate_result_gates()
    validate_test_specific_validation_tables()
    validate_q3d_elemental_scope()
    validate_pde_limit_calculations()
    validate_q14_method_setup_check()
    validate_report_formatting()
    print("ToxiGuard calculation validation passed")


if __name__ == "__main__":
    main()

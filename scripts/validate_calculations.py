from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import calculate_sample_prep, evaluate_lod_linearity, evaluate_rule, format_report_diff, format_report_number


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
    validate_report_formatting()
    print("ToxiGuard calculation validation passed")


if __name__ == "__main__":
    main()

from __future__ import annotations

from html import escape
from typing import Any

import pandas as pd
import streamlit as st


APP_BUILD = "q14-method-risk-check-2026-07-01"


Q14_STATUS_OPTIONS = ["Defined", "Partial", "Gap", "N/A"]


Q14_ANALYTICAL_PROCEDURE_CHECKS: list[dict[str, str]] = [
    {
        "Q14 check": "ATP and intended purpose",
        "Status": "Partial",
        "Risk": "High",
        "Problem signal": "The method has validation results, but the measurement objective, CQA, reportable result, range, and decision use are not written as an ATP.",
        "Evidence to request": "Analytical target profile or equivalent rationale linking CQA, intended purpose, performance criteria, and reportable range.",
        "CTD update": "3.2.P.5.2 / 3.2.P.5.3 / 3.2.P.5.6",
        "Q14 anchor": "ATP drives technology choice and validation performance criteria.",
    },
    {
        "Q14 check": "Attribute and matrix definition",
        "Status": "Partial",
        "Risk": "High",
        "Problem signal": "API, placebo, excipient, degradation product, dissolution medium, digestion matrix, or trace-level matrix effect is not explicitly covered.",
        "Evidence to request": "Matrix map, specificity/selectivity design, forced degradation or interference justification, and representative sample set.",
        "CTD update": "3.2.P.5.2 / 3.2.P.5.3",
        "Q14 anchor": "Procedure should measure the intended attribute with needed specificity/selectivity.",
    },
    {
        "Q14 check": "Technology and apparatus selection",
        "Status": "Partial",
        "Risk": "Medium",
        "Problem signal": "HPLC/UPLC/ICP/LC-MS/GC-MS/dissolution apparatus was chosen without explaining why it is fit for the product and operating environment.",
        "Evidence to request": "Technology selection rationale, detector sensitivity rationale, apparatus/column/source selection basis, and operating environment assumptions.",
        "CTD update": "3.2.P.2 / 3.2.P.5.2",
        "Q14 anchor": "ATP and operating environment inform technology selection.",
    },
    {
        "Q14 check": "Calibration model and reportable range",
        "Status": "Partial",
        "Risk": "High",
        "Problem signal": "R2 passes but intercept, weighting, low-level range, LOD/LOQ, or range relative to the specification/PDE/AI level is not justified.",
        "Evidence to request": "Calibration model, weighting rationale, intercept assessment, residuals, lower/upper range justification, and LOD/LOQ versus reference level.",
        "CTD update": "3.2.P.5.3 / 3.2.P.5.6",
        "Q14 anchor": "Performance should be shown over the reportable range including calibration model and range limits.",
    },
    {
        "Q14 check": "Critical procedure parameters",
        "Status": "Gap",
        "Risk": "High",
        "Problem signal": "pH, mobile phase, flow, column temperature, extraction, digestion, filter, wavelength, MS transition, or dissolution condition impacts are not ranked.",
        "Evidence to request": "Risk assessment or prior-knowledge table identifying procedure parameters that can impact performance.",
        "CTD update": "3.2.P.5.2 / 3.2.P.5.3",
        "Q14 anchor": "Risk management should identify parameters that can impact procedure performance.",
    },
    {
        "Q14 check": "Robustness and parameter ranges",
        "Status": "Partial",
        "Risk": "High",
        "Problem signal": "Robustness is tested as a checklist, but parameter ranges, interactions, MODR/PAR, or edge-of-range behavior are unclear.",
        "Evidence to request": "Robustness design, DoE or univariate range study, challenged parameters, acceptance criteria, and confirmed operating ranges.",
        "CTD update": "3.2.P.5.3 / 3.2.P.5.6",
        "Q14 anchor": "Robustness and analytical procedure parameter ranges support procedure understanding.",
    },
    {
        "Q14 check": "Analytical procedure control strategy",
        "Status": "Partial",
        "Risk": "High",
        "Problem signal": "System suitability, SST failure action, solution stability, blank/carryover, integration, sequence, sample hold, or re-injection rules are incomplete.",
        "Evidence to request": "Procedure control strategy covering SST, sample/standard stability, blank controls, carryover, sequence controls, integration, and failure handling.",
        "CTD update": "3.2.P.5.2 / 3.2.P.5.3",
        "Q14 anchor": "Procedure control strategy should maintain performance in routine use.",
    },
    {
        "Q14 check": "Established conditions and lifecycle change",
        "Status": "Gap",
        "Risk": "Medium",
        "Problem signal": "Which method parameters are regulatory commitments, which are operational ranges, and what change category applies are not defined.",
        "Evidence to request": "EC/PAR/MODR or lifecycle change table with reporting category, comparability expectation, and revalidation trigger.",
        "CTD update": "3.2.P.5.2 / 3.2.P.5.3 / lifecycle management",
        "Q14 anchor": "Enhanced understanding can support ECs and lifecycle change management.",
    },
    {
        "Q14 check": "Transfer and comparability strategy",
        "Status": "Partial",
        "Risk": "Medium",
        "Problem signal": "Method transfer depends only on acceptance criteria without representative samples, reference materials, or comparability logic.",
        "Evidence to request": "Transfer protocol, representative samples/reference materials, affected performance characteristics, and comparability criteria.",
        "CTD update": "3.2.P.5.3 / site transfer package",
        "Q14 anchor": "Changes and transfers should evaluate affected performance characteristics and comparability.",
    },
]


ELEMENTAL_IMPURITY_ELEMENTS: list[dict[str, Any]] = [
    {"Element": "As", "Class": "Class 1", "Scope": "Core 7", "Oral PDE (ug/day)": 15.0, "Parenteral PDE (ug/day)": 15.0, "Inhalation PDE (ug/day)": 2.0, "Risk question": "Toxic element; evaluate all potential API, excipient, equipment, water, and container sources."},
    {"Element": "Cd", "Class": "Class 1", "Scope": "Core 7", "Oral PDE (ug/day)": 5.0, "Parenteral PDE (ug/day)": 2.0, "Inhalation PDE (ug/day)": 3.0, "Risk question": "Toxic element; evaluate all potential API, excipient, equipment, water, and container sources."},
    {"Element": "Hg", "Class": "Class 1", "Scope": "Core 7", "Oral PDE (ug/day)": 30.0, "Parenteral PDE (ug/day)": 3.0, "Inhalation PDE (ug/day)": 1.0, "Risk question": "Toxic element; evaluate all potential API, excipient, equipment, water, and container sources."},
    {"Element": "Pb", "Class": "Class 1", "Scope": "Core 7", "Oral PDE (ug/day)": 5.0, "Parenteral PDE (ug/day)": 5.0, "Inhalation PDE (ug/day)": 5.0, "Risk question": "Toxic element; evaluate all potential API, excipient, equipment, water, and container sources."},
    {"Element": "Co", "Class": "Class 2A", "Scope": "Core 7", "Oral PDE (ug/day)": 50.0, "Parenteral PDE (ug/day)": 5.0, "Inhalation PDE (ug/day)": 3.0, "Risk question": "Naturally occurring or process-related risk; usually included in broad Q3D screening."},
    {"Element": "Ni", "Class": "Class 2A", "Scope": "Core 7", "Oral PDE (ug/day)": 200.0, "Parenteral PDE (ug/day)": 20.0, "Inhalation PDE (ug/day)": 6.0, "Risk question": "Catalyst, stainless steel, or excipient/source risk; usually included in broad Q3D screening."},
    {"Element": "V", "Class": "Class 2A", "Scope": "Core 7", "Oral PDE (ug/day)": 100.0, "Parenteral PDE (ug/day)": 10.0, "Inhalation PDE (ug/day)": 1.0, "Risk question": "Naturally occurring or catalyst/source risk; usually included in broad Q3D screening."},
    {"Element": "Ag", "Class": "Class 2B", "Scope": "Full 24", "Oral PDE (ug/day)": 150.0, "Parenteral PDE (ug/day)": 15.0, "Inhalation PDE (ug/day)": 7.0, "Risk question": "Assess if intentionally added, catalyst-related, or source-specific risk is present."},
    {"Element": "Au", "Class": "Class 2B", "Scope": "Full 24", "Oral PDE (ug/day)": 300.0, "Parenteral PDE (ug/day)": 300.0, "Inhalation PDE (ug/day)": 3.0, "Risk question": "Assess if intentionally added, catalyst-related, or source-specific risk is present."},
    {"Element": "Ir", "Class": "Class 2B", "Scope": "Full 24", "Oral PDE (ug/day)": 100.0, "Parenteral PDE (ug/day)": 10.0, "Inhalation PDE (ug/day)": 1.0, "Risk question": "Assess if intentionally added, catalyst-related, or source-specific risk is present."},
    {"Element": "Os", "Class": "Class 2B", "Scope": "Full 24", "Oral PDE (ug/day)": 100.0, "Parenteral PDE (ug/day)": 10.0, "Inhalation PDE (ug/day)": 1.0, "Risk question": "Assess if intentionally added, catalyst-related, or source-specific risk is present."},
    {"Element": "Pd", "Class": "Class 2B", "Scope": "Full 24", "Oral PDE (ug/day)": 100.0, "Parenteral PDE (ug/day)": 10.0, "Inhalation PDE (ug/day)": 1.0, "Risk question": "Assess if intentionally added, catalyst-related, or source-specific risk is present."},
    {"Element": "Pt", "Class": "Class 2B", "Scope": "Full 24", "Oral PDE (ug/day)": 100.0, "Parenteral PDE (ug/day)": 10.0, "Inhalation PDE (ug/day)": 1.0, "Risk question": "Assess if intentionally added, catalyst-related, or source-specific risk is present."},
    {"Element": "Rh", "Class": "Class 2B", "Scope": "Full 24", "Oral PDE (ug/day)": 100.0, "Parenteral PDE (ug/day)": 10.0, "Inhalation PDE (ug/day)": 1.0, "Risk question": "Assess if intentionally added, catalyst-related, or source-specific risk is present."},
    {"Element": "Ru", "Class": "Class 2B", "Scope": "Full 24", "Oral PDE (ug/day)": 100.0, "Parenteral PDE (ug/day)": 10.0, "Inhalation PDE (ug/day)": 1.0, "Risk question": "Assess if intentionally added, catalyst-related, or source-specific risk is present."},
    {"Element": "Se", "Class": "Class 2B", "Scope": "Full 24", "Oral PDE (ug/day)": 150.0, "Parenteral PDE (ug/day)": 80.0, "Inhalation PDE (ug/day)": 130.0, "Risk question": "Assess if intentionally added, catalyst-related, or source-specific risk is present."},
    {"Element": "Tl", "Class": "Class 2B", "Scope": "Full 24", "Oral PDE (ug/day)": 8.0, "Parenteral PDE (ug/day)": 8.0, "Inhalation PDE (ug/day)": 8.0, "Risk question": "Assess if intentionally added, catalyst-related, or source-specific risk is present."},
    {"Element": "Ba", "Class": "Class 3", "Scope": "Full 24", "Oral PDE (ug/day)": 1400.0, "Parenteral PDE (ug/day)": 700.0, "Inhalation PDE (ug/day)": 300.0, "Risk question": "Lower oral toxicity class; evaluate route and formulation/source-specific risk."},
    {"Element": "Cr", "Class": "Class 3", "Scope": "Full 24", "Oral PDE (ug/day)": 11000.0, "Parenteral PDE (ug/day)": 1100.0, "Inhalation PDE (ug/day)": 3.0, "Risk question": "Lower oral toxicity class; evaluate route and formulation/source-specific risk."},
    {"Element": "Cu", "Class": "Class 3", "Scope": "Full 24", "Oral PDE (ug/day)": 3000.0, "Parenteral PDE (ug/day)": 300.0, "Inhalation PDE (ug/day)": 30.0, "Risk question": "Lower oral toxicity class; evaluate route and formulation/source-specific risk."},
    {"Element": "Li", "Class": "Class 3", "Scope": "Full 24", "Oral PDE (ug/day)": 550.0, "Parenteral PDE (ug/day)": 250.0, "Inhalation PDE (ug/day)": 25.0, "Risk question": "Lower oral toxicity class; evaluate route and formulation/source-specific risk."},
    {"Element": "Mo", "Class": "Class 3", "Scope": "Full 24", "Oral PDE (ug/day)": 3000.0, "Parenteral PDE (ug/day)": 1500.0, "Inhalation PDE (ug/day)": 10.0, "Risk question": "Lower oral toxicity class; evaluate route and formulation/source-specific risk."},
    {"Element": "Sb", "Class": "Class 3", "Scope": "Full 24", "Oral PDE (ug/day)": 1200.0, "Parenteral PDE (ug/day)": 90.0, "Inhalation PDE (ug/day)": 20.0, "Risk question": "Lower oral toxicity class; evaluate route and formulation/source-specific risk."},
    {"Element": "Sn", "Class": "Class 3", "Scope": "Full 24", "Oral PDE (ug/day)": 6000.0, "Parenteral PDE (ug/day)": 600.0, "Inhalation PDE (ug/day)": 60.0, "Risk question": "Lower oral toxicity class; evaluate route and formulation/source-specific risk."},
]


Q3D_ROUTE_COLUMNS = {
    "Oral": "Oral PDE (ug/day)",
    "Parenteral": "Parenteral PDE (ug/day)",
    "Inhalation": "Inhalation PDE (ug/day)",
}


def _route_pde(item: dict[str, Any], route: str) -> float:
    return float(item.get(Q3D_ROUTE_COLUMNS.get(route, "Oral PDE (ug/day)"), item["Oral PDE (ug/day)"]))


def elemental_scope_frame(scope: str = "core7", route: str = "Oral") -> pd.DataFrame:
    full_scope = scope == "full24"
    rows: list[dict[str, Any]] = []
    for item in ELEMENTAL_IMPURITY_ELEMENTS:
        include = full_scope or item["Scope"] == "Core 7"
        route_pde = _route_pde(item, route)
        rows.append(
            {
                "Include": include,
                "Element": item["Element"],
                "ICH Q3D class": item["Class"],
                "Default scope": item["Scope"],
                "Source / risk question": item["Risk question"],
                "Route": route,
                "Route PDE entered (ug/day)": route_pde,
                "Control target / J-value note": "Q3D Table A.2.1 default; edit if product-specific route/PDE justification applies",
                "LOQ / target (%)": 10.0 if include else 0.0,
                "Spike recovery (%)": 92.0 if include else 0.0,
                "Precision RSD (%)": 12.0 if include else 0.0,
                "Note": "Q3D risk assessment + method validation raw data required" if include else "Add if product/source risk applies",
            }
        )
    return pd.DataFrame(rows)


def pde_concentration_limits(pde_ug_day: float, daily_intake_g_day: float) -> dict[str, float | None]:
    if pde_ug_day <= 0 or daily_intake_g_day <= 0:
        return {
            "permitted_conc_ug_g": None,
            "control_threshold_ug_day": None,
            "control_threshold_conc_ug_g": None,
        }
    permitted = pde_ug_day / daily_intake_g_day
    control_ug_day = pde_ug_day * 0.30
    return {
        "permitted_conc_ug_g": permitted,
        "control_threshold_ug_day": control_ug_day,
        "control_threshold_conc_ug_g": control_ug_day / daily_intake_g_day,
    }


def apply_q3d_pde_limits(frame: pd.DataFrame, daily_intake_g_day: float) -> pd.DataFrame:
    calculated = frame.copy()
    pde = pd.to_numeric(calculated["Route PDE entered (ug/day)"], errors="coerce")
    loq_pct = pd.to_numeric(calculated["LOQ / target (%)"], errors="coerce")
    if daily_intake_g_day > 0:
        calculated["Permitted concentration (ug/g)"] = pde / daily_intake_g_day
        calculated["Control threshold 30% PDE (ug/day)"] = pde * 0.30
        calculated["Control threshold concentration (ug/g)"] = (pde * 0.30) / daily_intake_g_day
        calculated["Calculated LOQ vs control threshold (ug/g)"] = calculated["Control threshold concentration (ug/g)"] * loq_pct / 100
    else:
        calculated["Permitted concentration (ug/g)"] = None
        calculated["Control threshold 30% PDE (ug/day)"] = None
        calculated["Control threshold concentration (ug/g)"] = None
        calculated["Calculated LOQ vs control threshold (ug/g)"] = None
    return calculated


def _tdi_percent(tdi_ug_day: float | None, mdd_mg_day: float) -> float | None:
    if tdi_ug_day is None or tdi_ug_day <= 0 or mdd_mg_day <= 0:
        return None
    return tdi_ug_day / (mdd_mg_day * 10.0)


def _lower_percent(percent_limit: float, tdi_ug_day: float | None, mdd_mg_day: float) -> tuple[float, str]:
    tdi_pct = _tdi_percent(tdi_ug_day, mdd_mg_day)
    if tdi_pct is None or percent_limit <= tdi_pct:
        return percent_limit, f"{percent_limit:g}%"
    return tdi_pct, f"{tdi_ug_day:g} ug/day TDI"


def q3b_threshold_frame(mdd_mg_day: float, impurity_pde_ug_day: float, sample_conc_mg_ml: float) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    reporting_pct = 0.1 if mdd_mg_day <= 1000 else 0.05
    rows.append({"Threshold": "Reporting", "Limit (%)": reporting_pct, "Basis": "ICH Q3B(R2): <=1 g 0.1%; >1 g 0.05%", "Gate": "Info"})

    if mdd_mg_day < 1:
        identification_pct, identification_basis = _lower_percent(1.0, 5.0, mdd_mg_day)
    elif mdd_mg_day <= 10:
        identification_pct, identification_basis = _lower_percent(0.5, 20.0, mdd_mg_day)
    elif mdd_mg_day <= 2000:
        identification_pct, identification_basis = _lower_percent(0.2, 2000.0, mdd_mg_day)
    else:
        identification_pct, identification_basis = 0.10, "0.10%"
    rows.append({"Threshold": "Identification", "Limit (%)": identification_pct, "Basis": f"ICH Q3B(R2): {identification_basis}", "Gate": "Info"})

    if mdd_mg_day < 10:
        qualification_pct, qualification_basis = _lower_percent(1.0, 50.0, mdd_mg_day)
    elif mdd_mg_day <= 100:
        qualification_pct, qualification_basis = _lower_percent(0.5, 200.0, mdd_mg_day)
    elif mdd_mg_day <= 2000:
        qualification_pct, qualification_basis = _lower_percent(0.2, 3000.0, mdd_mg_day)
    else:
        qualification_pct, qualification_basis = 0.15, "0.15%"
    rows.append({"Threshold": "Qualification", "Limit (%)": qualification_pct, "Basis": f"ICH Q3B(R2): {qualification_basis}", "Gate": "Info"})

    pde_pct = _tdi_percent(impurity_pde_ug_day, mdd_mg_day)
    if pde_pct is not None:
        rows.append({"Threshold": "Product-specific PDE/TDI", "Limit (%)": pde_pct, "Basis": f"Entered PDE/TDI {impurity_pde_ug_day:g} ug/day", "Gate": "Info"})
        recommended_pct = min(qualification_pct, pde_pct)
        recommended_basis = "Lower of ICH qualification threshold and entered product-specific PDE/TDI"
    else:
        recommended_pct = qualification_pct
        recommended_basis = "ICH qualification threshold; product-specific PDE/TDI not entered"
    rows.append({"Threshold": "Validation target", "Limit (%)": recommended_pct, "Basis": recommended_basis, "Gate": "Apply"})

    frame = pd.DataFrame(rows)
    if sample_conc_mg_ml > 0:
        frame["Method concentration (ug/mL)"] = sample_conc_mg_ml * 1000.0 * pd.to_numeric(frame["Limit (%)"], errors="coerce") / 100.0
    else:
        frame["Method concentration (ug/mL)"] = None
    return frame


PROFILES: list[dict[str, Any]] = [
    {
        "key": "assay",
        "ko": "함량",
        "en": "Assay",
        "tone": "#2867b2",
        "icon": "vial",
        "purpose": "API potency/water correction, label claim, and 100% reference concentration alignment.",
        "focus": "Prepare around the 100% label-claim concentration. Apply actual weighing, purity/water correction, stock volume, aliquot, final volume, and additional dilution.",
        "basis": "ICH Q2(R2), ICH Q14, ICH Q6A",
        "ctd": "3.2.P.5.2 / 3.2.P.5.3 / 3.2.P.5.6",
        "m14": "ICH M14 is not the analytical validation acceptance basis. Use it only as a safety-evidence traceability prompt when exposure or real-world safety interpretation is discussed.",
        "prep": [2.5, "ug/mL", 100.0, 25.0, 99.8, 100.0, 1.0, 50.0, 2.0],
        "lod": [0.05, 0.15, 0.9992, 12450.0, 240.0, 31125.0, 1867.5, 80.0],
        "rows": [
            ["Specificity interference", 0.12, "% of assay response", "lte", None, 0.2, "Blank/placebo/API impurity interference at assay retention time"],
            ["Linearity R2", 0.9992, "", "gte", 0.999, None, "Check intercept even when R2 passes"],
            ["Accuracy mean recovery", 99.1, "%", "between", 98.0, 102.0, "Usually evaluated around 80/100/120% assay levels"],
            ["Repeatability RSD", 1.1, "%", "lte", None, 2.0, "Six independent sample preparations"],
            ["Intermediate precision RSD", 1.8, "%", "lte", None, 2.0, "Different day, analyst, instrument, or column lot"],
            ["Robustness assay shift", 1.2, "%", "lte", None, 2.0, "Flow, wavelength, column temperature, mobile phase pH/composition"],
        ],
    },
    {
        "key": "related_substances",
        "ko": "유연물질",
        "en": "Related substances",
        "tone": "#b57900",
        "icon": "impurity",
        "purpose": "Control specified, unspecified, and degradation impurities against reporting, identification, and qualification thresholds.",
        "focus": "Reference concentration should match the impurity reporting or specification level, not only the assay 100% level. Low-level spike preparation and LOQ support are critical.",
        "basis": "ICH Q2(R2), ICH Q14, ICH Q3A(R2), ICH Q3B(R2)",
        "ctd": "3.2.P.5.2 / 3.2.P.5.3 / 3.2.P.5.5 / 3.2.P.5.6",
        "m14": "ICH M14 can support safety question framing if impurity exposure is connected to post-market or real-world safety evidence, but it does not replace impurity qualification or analytical validation rules.",
        "prep": [0.5, "ug/mL", 100.0, 5.0, 98.5, 100.0, 1.0, 100.0, 1.0],
        "lod": [0.01, 0.03, 0.9985, 9800.0, 68.0, 4900.0, 294.0, 50.0],
        "rows": [
            ["Critical pair resolution", 1.8, "Rs", "gte", 1.5, None, "API impurity, degradant, placebo, and nearest peak separation"],
            ["Linearity R2", 0.9985, "", "gte", 0.995, None, "LOQ to at least 120-150% of specification or reporting level"],
            ["LOQ precision RSD", 8.5, "%", "lte", None, 10.0, "Low-level repeat injections or preparations at LOQ"],
            ["Accuracy at threshold level", 92.0, "%", "between", 80.0, 120.0, "Recovery at reporting/identification/specification levels"],
            ["Repeatability RSD", 6.2, "%", "lte", None, 10.0, "Independent impurity sample preparations"],
            ["Forced degradation mass balance", 97.0, "%", "between", 95.0, 105.0, "Supports specificity and stability-indicating claim"],
        ],
    },
    {
        "key": "dissolution",
        "ko": "용출",
        "en": "Dissolution",
        "tone": "#087f86",
        "icon": "dissolution",
        "purpose": "Confirm the method can measure release performance and discriminate formulation or process changes.",
        "focus": "Reference concentration should reflect nominal concentration after complete dissolution or profile timepoint quantitation. Filter, medium, sink condition, and dilution scheme must be traceable.",
        "basis": "ICH Q2(R2), ICH Q14, ICH Q6A",
        "ctd": "3.2.P.2 / 3.2.P.5.2 / 3.2.P.5.3 / 3.2.P.5.6",
        "m14": "ICH M14 may help connect dissolution performance to clinical or real-world safety/effectiveness questions, but method validation is still judged by analytical and product-performance evidence.",
        "prep": [20.0, "ug/mL", 100.0, 20.0, 99.0, 100.0, 5.0, 50.0, 9.9],
        "lod": [0.2, 0.6, 0.9990, 8700.0, 320.0, 174000.0, 5220.0, 20.0],
        "rows": [
            ["Filter compatibility recovery", 99.0, "%", "between", 98.0, 102.0, "Filtered vs centrifuged or unfiltered reference solution"],
            ["Linearity R2", 0.9990, "", "gte", 0.995, None, "Range should cover early and late timepoint concentrations"],
            ["Accuracy mean recovery", 101.5, "%", "between", 95.0, 105.0, "Spike/recovery in dissolution medium"],
            ["Repeatability profile RSD", 4.2, "%", "lte", None, 5.0, "Typically stricter at later timepoints; early low release may justify wider review"],
            ["Intermediate precision mean difference", 6.5, "%", "lte", None, 10.0, "Different analyst/day/apparatus"],
            ["Discriminatory power", 1.0, "rank-order flag", "gte", 1.0, None, "Method should detect meaningful formulation or process change"],
        ],
    },
    {
        "key": "elemental_impurities",
        "ko": "금속불순물",
        "en": "Elemental impurities",
        "tone": "#2f7d46",
        "icon": "atom",
        "purpose": "Connect ICP method capability, PDE/control threshold, and product-specific risk assessment.",
        "focus": "Reference concentration should be connected to permitted daily exposure, maximum daily dose, and J/control threshold. Acid digestion and matrix spike recovery are central.",
        "basis": "ICH Q2(R2), ICH Q14, ICH Q3D(R2)",
        "ctd": "3.2.P.5.2 / 3.2.P.5.3 / 3.2.P.5.5 / 3.2.P.5.6",
        "m14": "ICH M14 can frame safety follow-up if elemental exposure is interpreted with real-world safety data. The CMC control decision remains anchored to Q3D and validated method capability.",
        "prep": [0.3, "ug/g or ppm", 100.0, 500.0, 100.0, 50.0, 1.0, 100.0, 333.3333],
        "lod": [0.01, 0.03, 0.9991, 6200.0, 8.0, 1860.0, 186.0, 30.0],
        "rows": [
            ["LOQ / control threshold", 10.0, "%", "lte", None, 30.0, "LOQ should be meaningfully below the J/control threshold"],
            ["Calibration R2", 0.9991, "", "gte", 0.995, None, "Matrix-matched or appropriately corrected calibration"],
            ["Spike recovery", 92.0, "%", "between", 70.0, 150.0, "Matrix spike recovery across representative elements"],
            ["Repeatability RSD", 12.0, "%", "lte", None, 20.0, "Independent digestions or preparations"],
            ["Intermediate precision RSD", 18.0, "%", "lte", None, 25.0, "Different day, analyst, instrument tune, or digestion batch"],
            ["Blank contribution", 12.0, "% of LOQ response", "lte", None, 20.0, "Reagent, vessel, and digestion blank control"],
        ],
    },
    {
        "key": "nitrosamines",
        "ko": "니트로사민",
        "en": "Nitrosamines",
        "tone": "#c45b1d",
        "icon": "molecule",
        "purpose": "Verify highly sensitive trace-level method performance against acceptable intake and product-specific nitrosamine risk.",
        "focus": "Reference concentration should be derived from acceptable intake, maximum daily dose, and sample concentration. Matrix effects, carryover, and isotope/internal standard performance are critical.",
        "basis": "ICH Q2(R2), ICH Q14, ICH M7(R2), health authority nitrosamine guidance",
        "ctd": "3.2.P.5.2 / 3.2.P.5.3 / 3.2.P.5.5 / 3.2.P.5.6",
        "m14": "ICH M14 is useful only as a safety-evidence connection layer when nitrosamine findings must be interpreted against real-world exposure or safety questions; it is not the CMC method validation rule.",
        "prep": [0.03, "ng/mL", 100.0, 100.0, 100.0, 100.0, 1.0, 100.0, 333.3333],
        "lod": [0.001, 0.003, 0.9988, 42000.0, 18.0, 1260.0, 126.0, 10.0],
        "rows": [
            ["Matrix interference at RT", 8.0, "% of LOQ response", "lte", None, 20.0, "Blank, placebo, API, excipient, and extraction solvent selectivity"],
            ["LOQ / acceptable intake level", 10.0, "%", "lte", None, 30.0, "Confirm LOQ is below the concentration derived from AI and maximum daily dose"],
            ["Linearity R2", 0.9988, "", "gte", 0.995, None, "Low ng/mL range; check intercept and weighting model"],
            ["Accuracy mean recovery", 88.0, "%", "between", 70.0, 130.0, "Evaluate near LOQ, AI-derived level, and upper validation level"],
            ["Precision RSD", 14.0, "%", "lte", None, 20.0, "Independent extraction and injection sequence"],
            ["Carryover after high standard", 6.0, "% of LOQ response", "lte", None, 20.0, "Critical for trace nitrosamine LC-MS/GC-MS methods"],
        ],
    },
]


ICONS = {
    "vial": '<path d="M9 2.8h6"/><path d="M10 2.8v5.5l-4.1 7.4A3.8 3.8 0 0 0 9.2 21h5.6a3.8 3.8 0 0 0 3.3-5.3L14 8.3V2.8"/><path d="M8 15h8"/>',
    "impurity": '<circle cx="7" cy="8" r="3"/><circle cx="16.5" cy="6.5" r="2.4"/><circle cx="15" cy="16" r="3.2"/><path d="m9.7 8.8 3.9 1.7"/><path d="m15.7 8.8-.4 3.9"/><path d="M7.8 10.8l4.6 3.4"/>',
    "dissolution": '<path d="M5 7h14"/><path d="M7 7v7.5A4.8 4.8 0 0 0 11.8 19h.4A4.8 4.8 0 0 0 17 14.5V7"/><path d="M8 13c1.2-1 2.5-1 3.8 0s2.7 1 4.2 0"/><path d="M10 3h4"/>',
    "atom": '<circle cx="12" cy="12" r="1.7"/><ellipse cx="12" cy="12" rx="8.5" ry="3.4"/><ellipse cx="12" cy="12" rx="8.5" ry="3.4" transform="rotate(60 12 12)"/><ellipse cx="12" cy="12" rx="8.5" ry="3.4" transform="rotate(120 12 12)"/>',
    "molecule": '<circle cx="5.8" cy="12" r="2.8"/><circle cx="15.8" cy="6.5" r="2.5"/><circle cx="17.6" cy="17.2" r="3"/><path d="m8.2 10.6 5.5-3"/><path d="m8.4 13.3 6.4 2.7"/><path d="M16.2 9.1l1 5.1"/>',
}


def _label(profile: dict[str, Any], lang: str) -> str:
    return str(profile["en"] if lang == "en" else profile["ko"])


def _rows(profile: dict[str, Any]) -> pd.DataFrame:
    return pd.DataFrame(profile["rows"], columns=["Item", "Result", "Unit", "Rule", "Lower", "Upper", "Note"])


def q14_problem_frame(test_item: str = "Analytical procedure") -> pd.DataFrame:
    frame = pd.DataFrame(Q14_ANALYTICAL_PROCEDURE_CHECKS)
    frame.insert(0, "Test item", test_item)
    return frame


def evaluate_q14_problem(row: pd.Series) -> str:
    status = str(row.get("Status", "")).strip()
    risk = str(row.get("Risk", "")).strip()
    if status == "Defined":
        return "Pass"
    if status == "N/A":
        return "Info"
    if status in {"Gap", "Partial"}:
        return "Review"
    if risk in {"High", "Medium"}:
        return "Review"
    return "Info"


def _profile(key: str) -> dict[str, Any]:
    return next((profile for profile in PROFILES if profile["key"] == key), PROFILES[0])


def _ensure_tables() -> dict[str, pd.DataFrame]:
    if "validation_ext_tables" not in st.session_state:
        st.session_state.validation_ext_tables = {profile["key"]: _rows(profile) for profile in PROFILES}
    for profile in PROFILES:
        st.session_state.validation_ext_tables.setdefault(profile["key"], _rows(profile))
    return st.session_state.validation_ext_tables


def _ensure_q14_tables() -> dict[str, pd.DataFrame]:
    if "q14_development_tables" not in st.session_state:
        st.session_state.q14_development_tables = {
            profile["key"]: q14_problem_frame(_label(profile, "en")) for profile in PROFILES
        }
    for profile in PROFILES:
        st.session_state.q14_development_tables.setdefault(profile["key"], q14_problem_frame(_label(profile, "en")))
    return st.session_state.q14_development_tables


def _element_gate(row: pd.Series) -> str:
    if not bool(row.get("Include", False)):
        return "N/A"
    pde = pd.to_numeric(row.get("Route PDE entered (ug/day)"), errors="coerce")
    loq_pct = pd.to_numeric(row.get("LOQ / target (%)"), errors="coerce")
    recovery = pd.to_numeric(row.get("Spike recovery (%)"), errors="coerce")
    rsd = pd.to_numeric(row.get("Precision RSD (%)"), errors="coerce")
    if pd.isna(pde) or pde <= 0 or pd.isna(loq_pct) or pd.isna(recovery) or pd.isna(rsd):
        return "Review"
    if loq_pct > 30:
        return "Review"
    if recovery < 70 or recovery > 150:
        return "Review"
    if rsd > 20:
        return "Review"
    return "Pass"


def _svg(body: str) -> str:
    return f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">{body}</svg>'


def apply_validation_extension(app: Any) -> None:
    app.APP_BUILD = APP_BUILD
    app.ICON_SVG.update(ICONS)
    app.TEXT["ko"]["calc_help"] = "ICH Q14 분석법 설정 문제점, 시료 제조 농도, 결과 gate를 시험항목별로 검토합니다."
    app.TEXT["en"]["calc_help"] = "Review ICH Q14 method setup risks, sample preparation, and result gates by test item."

    original_initialize_state = app.initialize_state
    original_response_rows = app.response_rows
    original_build_decision_packet = app.build_decision_packet

    def initialize_state() -> None:
        original_initialize_state()
        st.session_state.setdefault("validation_test_item", "assay")
        _ensure_tables()
        _ensure_q14_tables()

    def review_frame(include_gate: bool = True) -> pd.DataFrame:
        tables = _ensure_tables()
        frames = []
        for profile in PROFILES:
            df = tables[profile["key"]].copy().drop(columns=["Gate"], errors="ignore")
            df.insert(0, "Test item", _label(profile, "en"))
            df["CTD update"] = profile["ctd"]
            df["Regulatory basis"] = profile["basis"]
            if include_gate:
                df["Gate"] = df.apply(app.evaluate_rule, axis=1)
            frames.append(df)
        return pd.concat(frames, ignore_index=True)

    def summary_frame() -> pd.DataFrame:
        rows = []
        tables = _ensure_tables()
        for profile in PROFILES:
            df = tables[profile["key"]].copy()
            df["Gate"] = df.apply(app.evaluate_rule, axis=1)
            review_count = int((df["Gate"] == "Review").sum())
            rows.append(
                {
                    "Test item": _label(profile, "en"),
                    "Gate": "Review" if review_count else "Pass",
                    "Review items": review_count,
                    "Regulatory basis": profile["basis"],
                    "CTD update": profile["ctd"],
                }
            )
        return pd.DataFrame(rows)

    def q14_report_frame(include_gate: bool = True) -> pd.DataFrame:
        tables = _ensure_q14_tables()
        frames = []
        for profile in PROFILES:
            df = tables[profile["key"]].copy().drop(columns=["Gate"], errors="ignore")
            df["Test item"] = _label(profile, "en")
            if include_gate:
                df["Gate"] = df.apply(evaluate_q14_problem, axis=1)
            frames.append(df)
        return pd.concat(frames, ignore_index=True)

    def render_q14_development_panel(profile: dict[str, Any]) -> pd.DataFrame:
        lang = str(st.session_state.get("lang", "ko"))
        app.mini_heading(
            "ICH Q14 analytical procedure development check" if lang == "en" else "ICH Q14 분석법 설정 문제점",
            "alert",
            "orange",
        )
        st.info(
            "ICH Q14 lens: validation results alone are not enough. Confirm the ATP, procedure understanding, "
            "risk-ranked parameters, robustness/ranges, control strategy, and lifecycle change logic before treating the method as submission-ready."
            if lang == "en"
            else "ICH Q14 관점에서는 밸리데이션 결과만으로 충분하지 않습니다. 제출 가능한 분석법으로 보기 전에 ATP, 분석법 이해도, risk-ranked parameter, robustness/range, control strategy, lifecycle change logic을 확인해야 합니다."
        )
        tables = _ensure_q14_tables()
        selected_key = str(profile["key"])
        status_col = app.COLUMN_KO.get("Status", "Status") if lang == "ko" else "Status"
        risk_col = app.COLUMN_KO.get("Risk", "Risk") if lang == "ko" else "Risk"
        edited = app.delocalize_dataframe(
            st.data_editor(
            app.localize_dataframe(tables[selected_key], lang),
            width="stretch",
            num_rows="dynamic",
            key=f"q14_editor_{selected_key}",
            column_config={
                status_col: st.column_config.SelectboxColumn(status_col, options=app.option_labels(Q14_STATUS_OPTIONS, lang), required=True),
                risk_col: st.column_config.SelectboxColumn(risk_col, options=app.option_labels(["High", "Medium", "Low"], lang), required=True),
            },
            ),
            lang,
        )
        edited = edited.copy().drop(columns=["Gate"], errors="ignore")
        edited["Gate"] = edited.apply(evaluate_q14_problem, axis=1)
        tables[selected_key] = edited.drop(columns=["Gate"], errors="ignore")
        st.session_state.q14_development_tables = tables

        review = edited[edited["Gate"] == "Review"]
        high_review_count = int(((review["Risk"] == "High") & (review["Status"].isin(["Gap", "Partial"]))).sum())
        lifecycle_review_count = int(
            (
                edited["Q14 check"].astype(str).str.contains("lifecycle", case=False)
                & (edited["Gate"] == "Review")
            ).sum()
        )
        metrics = st.columns(4)
        metrics[0].metric("Q14 review items" if lang == "en" else "Q14 검토 항목", str(len(review)))
        metrics[1].metric("High-risk gaps" if lang == "en" else "고위험 gap", str(high_review_count))
        metrics[2].metric("Defined controls" if lang == "en" else "정의된 control", str(int((edited["Status"] == "Defined").sum())))
        metrics[3].metric("Lifecycle gaps" if lang == "en" else "Lifecycle gap", str(lifecycle_review_count))

        st.dataframe(app.display_dataframe(edited, lang), width="stretch", hide_index=True)
        if len(review):
            st.warning(
                "Q14 review is triggered: the method may validate numerically but still lack development rationale or lifecycle control."
                if lang == "en"
                else "Q14 검토가 필요합니다. 수치상 밸리데이션은 통과해도 분석법 개발 근거 또는 lifecycle control이 부족할 수 있습니다."
            )
            st.dataframe(
                app.display_dataframe(review, lang, ["Q14 check", "Status", "Risk", "Problem signal", "Evidence to request", "CTD update"]),
                width="stretch",
                hide_index=True,
            )
        else:
            st.success(
                "Q14 analytical procedure development check is passing for the selected test item."
                if lang == "en"
                else "선택한 시험항목의 Q14 분석법 개발 검토가 통과 상태입니다."
            )
        return edited

    def concentration_review(profile: dict[str, Any]) -> dict[str, Any]:
        lang = str(st.session_state.get("lang", "ko"))
        ref, unit_default, level, weighed, purity, stock_volume, aliquot, final_volume, dilution = profile["prep"]
        prefix = f"ext_prep_{profile['key']}"
        st.caption(app.profile_copy(profile, "focus", lang))
        c1, c2, c3 = st.columns(3)
        with c1:
            reference_conc = st.number_input("Reference concentration at 100%" if lang == "en" else "100% 기준농도", min_value=0.000001, value=float(ref), step=0.1, format="%.6f", key=f"{prefix}_ref")
            unit = st.text_input("Concentration unit" if lang == "en" else "농도 단위", value=str(unit_default), key=f"{prefix}_unit")
            level_pct = st.number_input("Validation level %" if lang == "en" else "밸리데이션 level %", min_value=0.0, value=float(level), step=5.0, key=f"{prefix}_level")
        with c2:
            weighed_mg = st.number_input("Actual weighed amount (mg)" if lang == "en" else "실제 칭량량 (mg)", min_value=0.0, value=float(weighed), step=0.1, format="%.4f", key=f"{prefix}_weighed")
            purity_pct = st.number_input("Purity / potency correction %" if lang == "en" else "순도 / 역가 보정 %", min_value=0.0, value=float(purity), step=0.1, format="%.4f", key=f"{prefix}_purity")
            stock_volume_ml = st.number_input("Stock final volume (mL)" if lang == "en" else "Stock 최종부피 (mL)", min_value=0.000001, value=float(stock_volume), step=10.0, format="%.4f", key=f"{prefix}_stock")
        with c3:
            aliquot_ml = st.number_input("Aliquot taken from stock (mL)" if lang == "en" else "Stock에서 취한량 (mL)", min_value=0.0, value=float(aliquot), step=0.1, format="%.4f", key=f"{prefix}_aliquot")
            final_volume_ml = st.number_input("Final volume after aliquot (mL)" if lang == "en" else "희석 후 최종부피 (mL)", min_value=0.000001, value=float(final_volume), step=10.0, format="%.4f", key=f"{prefix}_final")
            dilution_factor = st.number_input("Additional dilution factor" if lang == "en" else "추가 희석배수", min_value=0.000001, value=float(dilution), step=0.5, format="%.4f", key=f"{prefix}_dilution")

        calc = app.calculate_sample_prep(reference_conc, level_pct, weighed_mg, purity_pct, stock_volume_ml, aliquot_ml, final_volume_ml, dilution_factor)
        metrics = st.columns(4)
        metrics[0].metric("Stock concentration" if lang == "en" else "Stock 농도", f"{float(calc['stock_conc']):.4f} {unit}")
        metrics[1].metric("Actual final concentration" if lang == "en" else "실제 최종농도", f"{float(calc['final_conc']):.4f} {unit}")
        metrics[2].metric("Target concentration" if lang == "en" else "목표 농도", f"{float(calc['target_conc']):.4f} {unit}")
        metrics[3].metric("Actual vs target" if lang == "en" else "목표 대비 차이", "N/A" if calc["diff_pct"] is None else f"{float(calc['diff_pct']):+.2f}%")
        if calc["gate"] == "Pass":
            st.success(app.localize_note(str(calc["message"]), lang))
        elif calc["gate"] == "Review":
            st.warning(app.localize_note(str(calc["message"]), lang))
        else:
            st.error(app.localize_note(str(calc["message"]), lang))
        return {"test_item": _label(profile, "en"), "reference_conc": reference_conc, "unit": unit, "final_conc": calc["final_conc"], "target_conc": calc["target_conc"], "diff_pct": calc["diff_pct"]}

    def lod_review(reference_conc: float, unit: str, profile: dict[str, Any]) -> list[str]:
        lang = str(st.session_state.get("lang", "ko"))
        app.mini_heading("LOD / LOQ and intercept risk" if lang == "en" else "LOD / LOQ 및 intercept 리스크", "trend", "orange")
        lod, loq, r2, slope, intercept, response_100, response_loq, lowest = profile["lod"]
        prefix = f"ext_lod_{profile['key']}"
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            lod = st.number_input("LOD", min_value=0.0, value=float(lod), step=0.01, format="%.6f", key=f"{prefix}_lod")
            loq = st.number_input("LOQ", min_value=0.0, value=float(loq), step=0.01, format="%.6f", key=f"{prefix}_loq")
        with c2:
            r2 = st.number_input("Linearity R2" if lang == "en" else "직선성 R2", min_value=0.0, max_value=1.0, value=float(r2), step=0.0001, format="%.6f", key=f"{prefix}_r2")
            st.number_input("Mean slope" if lang == "en" else "평균 slope", value=float(slope), step=100.0, format="%.4f", key=f"{prefix}_slope")
        with c3:
            intercept = st.number_input("Mean intercept" if lang == "en" else "평균 intercept", value=float(intercept), step=10.0, format="%.4f", key=f"{prefix}_intercept")
            response_100 = st.number_input("Response at 100%" if lang == "en" else "100% response", min_value=0.000001, value=float(response_100), step=100.0, format="%.4f", key=f"{prefix}_r100")
        with c4:
            response_loq = st.number_input("Response at LOQ" if lang == "en" else "LOQ response", min_value=0.000001, value=float(response_loq), step=50.0, format="%.4f", key=f"{prefix}_rloq")
            lowest = st.number_input("Lowest linearity level %" if lang == "en" else "최저 직선성 level %", min_value=0.0, value=float(lowest), step=5.0, key=f"{prefix}_lowest")
        result = app.evaluate_lod_linearity(reference_conc, lod, loq, r2, intercept, response_100, response_loq, lowest)
        cols = st.columns(4)
        cols[0].metric("LOD / reference" if lang == "en" else "LOD / 기준농도", f"{float(result['lod_pct']):.2f}%")
        cols[1].metric("LOQ / reference" if lang == "en" else "LOQ / 기준농도", f"{float(result['loq_pct']):.2f}%")
        cols[2].metric("Intercept / 100% response" if lang == "en" else "Intercept / 100% response", f"{float(result['intercept_100_pct']):.2f}%")
        cols[3].metric("Intercept / LOQ response" if lang == "en" else "Intercept / LOQ response", f"{float(result['intercept_loq_pct']):.2f}%")
        notes = list(result["notes"])
        app.mini_heading(app.tr(st.session_state.lang, "risk_notes"), "alert", "orange")
        for note in notes:
            st.success(app.localize_note(note, lang)) if "acceptable" in note else st.warning(app.localize_note(note, lang))
        return [f"{_label(profile, 'en')}: LOD {lod:.6f} {unit}", f"{_label(profile, 'en')}: LOQ {loq:.6f} {unit}", *notes]

    def render_related_pde_panel() -> pd.DataFrame:
        lang = str(st.session_state.get("lang", "ko"))
        app.mini_heading("Related substance PDE/TDI limit" if lang == "en" else "유연물질 PDE/TDI 기준량", "impurity", "gold")
        st.info(
            "ICH Q3B(R2) applies reporting, identification, and qualification thresholds by maximum daily dose. "
            "If a product-specific PDE/TDI or acceptable intake is lower, use that value to calculate the validation target."
            if lang == "en"
            else "ICH Q3B(R2)는 최대일일복용량에 따라 reporting, identification, qualification threshold를 적용합니다. 제품별 PDE/TDI 또는 acceptable intake가 더 낮다면 그 값을 기준으로 밸리데이션 target을 계산해야 합니다."
        )
        c1, c2, c3 = st.columns(3)
        with c1:
            mdd_mg_day = st.number_input(
                "Maximum daily dose of drug substance (mg/day)" if lang == "en" else "원료의약품 최대일일복용량 (mg/day)",
                min_value=0.000001,
                value=50.0,
                step=10.0,
                format="%.6f",
                key="related_mdd_mg_day",
            )
        with c2:
            impurity_pde_ug_day = st.number_input(
                "Product-specific impurity PDE/TDI (ug/day)" if lang == "en" else "제품별 유연물질 PDE/TDI (ug/day)",
                min_value=0.0,
                value=200.0,
                step=10.0,
                format="%.6f",
                key="related_impurity_pde_ug_day",
            )
        with c3:
            sample_conc_mg_ml = st.number_input(
                "Main sample concentration at 100% (mg/mL)" if lang == "en" else "100% 주시료 농도 (mg/mL)",
                min_value=0.000001,
                value=0.5,
                step=0.1,
                format="%.6f",
                key="related_sample_conc_mg_ml",
            )

        frame = q3b_threshold_frame(mdd_mg_day, impurity_pde_ug_day, sample_conc_mg_ml)
        target = frame[frame["Threshold"] == "Validation target"].iloc[0]
        metrics = st.columns(4)
        metrics[0].metric("Validation target" if lang == "en" else "밸리데이션 target", f"{float(target['Limit (%)']):.4f}%")
        metrics[1].metric("Target concentration" if lang == "en" else "Target 농도", f"{float(target['Method concentration (ug/mL)']):.4f} ug/mL")
        metrics[2].metric("MDD", f"{mdd_mg_day:.4g} mg/day")
        metrics[3].metric("PDE/TDI", f"{impurity_pde_ug_day:.4g} ug/day" if impurity_pde_ug_day > 0 else "Not entered")
        st.dataframe(app.display_dataframe(frame, lang), width="stretch", hide_index=True)
        st.session_state.related_pde_frame = frame
        if st.button("Apply calculated reference concentration to sample prep" if lang == "en" else "계산된 기준농도를 시료 제조에 적용", key="apply_related_pde_ref", use_container_width=True):
            st.session_state["ext_prep_related_substances_ref"] = float(target["Method concentration (ug/mL)"])
            st.session_state["ext_prep_related_substances_unit"] = "ug/mL"
            st.session_state["ext_prep_related_substances_level"] = 100.0
            st.rerun()
        return frame

    def render_elemental_scope_panel() -> None:
        lang = str(st.session_state.get("lang", "ko"))
        app.mini_heading("ICH Q3D elemental impurity scope" if lang == "en" else "ICH Q3D 금속불순물 범위", "atom", "green")
        c_route, c_mdd = st.columns(2)
        with c_route:
            route = st.selectbox("Route of administration" if lang == "en" else "투여경로", ["Oral", "Parenteral", "Inhalation"], key="q3d_route")
        with c_mdd:
            daily_intake_g_day = st.number_input(
                "Maximum daily product intake (g/day)" if lang == "en" else "완제 최대일일복용량 (g/day)",
                min_value=0.000001,
                value=2.5,
                step=0.5,
                format="%.6f",
                key="q3d_daily_intake_g_day",
            )
        mode = st.radio(
            "Q3D scope mode" if lang == "en" else "Q3D 검토 범위",
            ["Core 7: Class 1 + Class 2A", "Full Q3D 24 elements"],
            horizontal=True,
            key="q3d_scope_mode",
        )
        scope_key = "full24" if mode.startswith("Full") else "core7"
        previous_scope = st.session_state.get("q3d_scope_key")
        previous_route = st.session_state.get("q3d_scope_route")
        if previous_scope != scope_key or previous_route != route or "q3d_element_df" not in st.session_state:
            st.session_state.q3d_scope_key = scope_key
            st.session_state.q3d_scope_route = route
            st.session_state.q3d_element_df = elemental_scope_frame(scope_key, route)

        element_df = apply_q3d_pde_limits(st.session_state.q3d_element_df.copy(), daily_intake_g_day)
        element_df["Gate"] = element_df.apply(_element_gate, axis=1)
        included = element_df[element_df["Include"]]
        class_counts = included["ICH Q3D class"].value_counts().to_dict()
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Included elements" if lang == "en" else "포함 원소", f"{len(included)} / 24")
        c2.metric("Class 1", str(class_counts.get("Class 1", 0)))
        c3.metric("Class 2A", str(class_counts.get("Class 2A", 0)))
        c4.metric("Gate review" if lang == "en" else "Gate 검토", str(int((included["Gate"] == "Review").sum())))

        st.info(
            "Q3D practical read: Core 7 covers Class 1 (As, Cd, Hg, Pb) plus Class 2A "
            "(Co, Ni, V). Full Q3D screening expands to all 24 elements including Class 2B and Class 3. "
            "Permitted concentration is calculated as PDE (ug/day) / maximum daily product intake (g/day)."
            if lang == "en"
            else "Q3D 실무 해석: Core 7은 Class 1(As, Cd, Hg, Pb)과 Class 2A(Co, Ni, V)를 포함합니다. Full Q3D screening은 Class 2B와 Class 3를 포함한 24종 전체로 확장됩니다. 허용농도는 PDE(ug/day) / 완제 최대일일복용량(g/day)으로 계산합니다."
        )
        edited_elements = st.data_editor(
            element_df.drop(
                columns=[
                    "Gate",
                    "Permitted concentration (ug/g)",
                    "Control threshold 30% PDE (ug/day)",
                    "Control threshold concentration (ug/g)",
                    "Calculated LOQ vs control threshold (ug/g)",
                ],
                errors="ignore",
            ),
            width="stretch",
            num_rows="fixed",
            key="q3d_element_editor",
            column_config={
                "Include": st.column_config.CheckboxColumn("Include", help="Include this element in the validation scope"),
                "ICH Q3D class": st.column_config.SelectboxColumn(
                    "ICH Q3D class", options=["Class 1", "Class 2A", "Class 2B", "Class 3"], required=True
                ),
                "Route PDE entered (ug/day)": st.column_config.NumberColumn("Route PDE entered (ug/day)", min_value=0.0, step=1.0),
                "LOQ / target (%)": st.column_config.NumberColumn("LOQ / target (%)", min_value=0.0, step=1.0),
                "Spike recovery (%)": st.column_config.NumberColumn("Spike recovery (%)", min_value=0.0, step=1.0),
                "Precision RSD (%)": st.column_config.NumberColumn("Precision RSD (%)", min_value=0.0, step=1.0),
            },
        )
        edited_elements = edited_elements.copy()
        edited_elements = apply_q3d_pde_limits(edited_elements, daily_intake_g_day)
        edited_elements["Gate"] = edited_elements.apply(_element_gate, axis=1)
        st.session_state.q3d_element_df = edited_elements.drop(
            columns=[
                "Gate",
                "Permitted concentration (ug/g)",
                "Control threshold 30% PDE (ug/day)",
                "Control threshold concentration (ug/g)",
                "Calculated LOQ vs control threshold (ug/g)",
            ],
            errors="ignore",
        )

        active = edited_elements[edited_elements["Include"]]
        st.dataframe(
            app.display_dataframe(
                active,
                lang,
                [
                    "Element",
                    "ICH Q3D class",
                    "Default scope",
                    "Route PDE entered (ug/day)",
                    "Permitted concentration (ug/g)",
                    "Control threshold concentration (ug/g)",
                    "LOQ / target (%)",
                    "Calculated LOQ vs control threshold (ug/g)",
                    "Spike recovery (%)",
                    "Precision RSD (%)",
                    "Gate",
                    "Note",
                ],
            ),
            width="stretch",
            hide_index=True,
        )
        if scope_key == "core7" and len(active) < 7:
            st.warning(
                "Core 7 mode should normally retain As, Cd, Hg, Pb, Co, Ni, and V unless a documented product risk rationale excludes an element."
                if lang == "en"
                else "Core 7 모드에서는 제품별 risk rationale이 문서화되어 제외되지 않는 한 As, Cd, Hg, Pb, Co, Ni, V를 유지하는 것이 일반적입니다."
            )
        if scope_key == "full24" and len(active) < 24:
            st.warning(
                "Full Q3D 24 mode is selected, but not all 24 elements are included. Confirm the exclusion rationale."
                if lang == "en"
                else "Full Q3D 24 모드가 선택되었지만 24종 전체가 포함되지 않았습니다. 제외 근거를 확인하세요."
            )

    def q3d_scope_report_frame() -> pd.DataFrame:
        if "q3d_element_df" not in st.session_state:
            frame = elemental_scope_frame("core7")
        else:
            frame = st.session_state.q3d_element_df.copy()
        daily_intake_g_day = float(st.session_state.get("q3d_daily_intake_g_day", 2.5))
        frame = apply_q3d_pde_limits(frame, daily_intake_g_day)
        frame["Gate"] = frame.apply(_element_gate, axis=1)
        return frame[frame["Include"]].copy()

    def related_pde_report_frame() -> pd.DataFrame:
        if "related_pde_frame" in st.session_state:
            return st.session_state.related_pde_frame.copy()
        return q3b_threshold_frame(50.0, 200.0, 0.5)

    def render_validation(lang: str) -> None:
        app.section_header(app.tr(lang, "validation"), app.tr(lang, "calc_help"), "calculator", "orange")
        st.markdown(
            """
            <style>
              .vcc-grid{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:10px;margin:10px 0}
              .vcc-card{min-height:154px;border:1px solid #d9e3ef;border-top:4px solid var(--tone);border-radius:8px;padding:12px;background:white;box-shadow:0 10px 24px rgba(7,27,61,.06)}
              .vcc-card strong{display:block;margin:8px 0 4px;color:#071b3d}.vcc-card p{font-size:.73rem;line-height:1.35;color:#5d6a7f;margin:0}
              .vcc-icon{display:grid;place-items:center;width:42px;height:42px;border-radius:8px;color:var(--tone);background:#f4fafb;border:1px solid #d9e3ef}.vcc-icon svg{width:25px;height:25px}
              .vcc-selected{background:linear-gradient(180deg,#fff2cf,#fff 74%);box-shadow:0 18px 34px rgba(7,27,61,.12)}
              .vcc-basis{margin:12px 0 14px;padding:15px 16px;border:1px solid #d9e3ef;border-left:5px solid var(--tone);border-radius:8px;background:#fff;color:#071b3d}
              @media(max-width:900px){.vcc-grid{grid-template-columns:1fr 1fr}}@media(max-width:640px){.vcc-grid{grid-template-columns:1fr}}
            </style>
            """,
            unsafe_allow_html=True,
        )
        app.mini_heading(app.tr(lang, "validation_select"), "shield", "orange")
        tables = _ensure_tables()
        current = st.session_state.get("validation_test_item", "assay")
        cards = []
        for profile in PROFILES:
            df = tables[profile["key"]].copy()
            df["Gate"] = df.apply(app.evaluate_rule, axis=1)
            review = int((df["Gate"] == "Review").sum())
            selected = " vcc-selected" if profile["key"] == current else ""
            cards.append(
                f'<article class="vcc-card{selected}" style="--tone:{profile["tone"]}">'
                f'<span class="vcc-icon">{_svg(ICONS[profile["icon"]])}</span>'
                f'<strong>{escape(_label(profile, lang))}</strong>'
                f'<p>{escape(app.profile_copy(profile, "purpose", lang))}</p>'
                f'<p>{review} {"review" if lang == "en" else "검토"}</p>'
                f'</article>'
            )
        st.markdown(f'<div class="vcc-grid">{"".join(cards)}</div>', unsafe_allow_html=True)
        cols = st.columns(len(PROFILES))
        for idx, profile in enumerate(PROFILES):
            item_label = _label(profile, lang)
            button_label = f"{item_label} {app.tr(lang, 'selected')}" if profile["key"] == current else (
                f"Open {item_label}" if lang == "en" else f"{item_label} {app.tr(lang, 'open_review')}"
            )
            with cols[idx]:
                if st.button(button_label, key=f"vcc_ext_{profile['key']}", use_container_width=True, type="primary" if profile["key"] == current else "secondary"):
                    st.session_state.validation_test_item = profile["key"]
                    st.rerun()

        profile = _profile(str(st.session_state.get("validation_test_item", "assay")))
        st.markdown(
            f'<div class="vcc-basis" style="--tone:{profile["tone"]}">'
            f'<strong>{escape(_label(profile, lang))} {escape(app.tr(lang, "validation_basis"))}</strong><br>'
            f'<b>{escape(app.tr(lang, "regulatory_basis"))}:</b> {escape(profile["basis"])}<br>'
            f'<b>{escape(app.tr(lang, "ctd_location"))}:</b> {escape(profile["ctd"])}<br>'
            f'<b>{escape(app.tr(lang, "m14_note"))}:</b> {escape(app.profile_copy(profile, "m14", lang))}'
            f'</div>',
            unsafe_allow_html=True,
        )
        render_q14_development_panel(profile)
        if profile["key"] == "related_substances":
            render_related_pde_panel()
        if profile["key"] == "elemental_impurities":
            render_elemental_scope_panel()
        app.mini_heading(app.tr(lang, "sample_prep"), "calculator", "orange")
        calc = concentration_review(profile)
        notes = lod_review(float(calc["reference_conc"]), str(calc["unit"]), profile)
        app.mini_heading(app.tr(lang, "validation_gate"), "shield", "orange")
        st.info(f"{app.tr(lang, 'result_inputs')} - {_label(profile, lang)}: {'; '.join(str(item) for item in tables[profile['key']]['Item'].tolist())}")
        rule_col = app.COLUMN_KO.get("Rule", "Rule") if lang == "ko" else "Rule"
        edited = app.delocalize_dataframe(
            st.data_editor(
                app.localize_dataframe(tables[profile["key"]], lang),
                width="stretch",
                num_rows="dynamic",
                column_config={rule_col: st.column_config.SelectboxColumn(rule_col, options=["between", "gte", "lte", "info"], required=True)},
                key=f"vcc_ext_editor_{profile['key']}",
            ),
            lang,
        )
        edited = edited.copy().drop(columns=["Gate"], errors="ignore")
        edited["Gate"] = edited.apply(app.evaluate_rule, axis=1)
        tables[profile["key"]] = edited.drop(columns=["Gate"], errors="ignore")
        st.session_state.validation_ext_tables = tables
        st.dataframe(app.display_dataframe(edited, lang), width="stretch", hide_index=True)
        review_count = int((edited["Gate"] == "Review").sum())
        st.warning(f"{review_count} {app.tr(lang, 'validation_review_warning')}") if review_count else st.success(app.tr(lang, "validation_review_success"))
        app.mini_heading(app.tr(lang, "overall_validation_summary"), "trend", "orange")
        st.dataframe(app.display_dataframe(summary_frame(), lang), width="stretch", hide_index=True)
        st.session_state["last_calc"] = calc
        st.session_state["last_risk_notes"] = notes

    def response_rows() -> pd.DataFrame:
        rows = original_response_rows()
        reviews = review_frame(include_gate=True)
        additions = []
        for _, row in reviews[reviews["Gate"] == "Review"].head(10).iterrows():
            additions.append(
                {
                    "Question": f"Please provide raw data and sample-preparation rationale for {row['Test item']} - {row['Item']}.",
                    "Triggered by": f"Validation gate review: {row['Result']} {row['Unit']} / rule {row['Rule']}",
                    "Evidence needed": str(row["Note"]),
                    "CTD update": str(row["CTD update"]),
                    "Owner": "Analytical / CMC RA",
                }
            )
        q14_reviews = q14_report_frame(include_gate=True)
        for _, row in q14_reviews[q14_reviews["Gate"] == "Review"].head(12).iterrows():
            additions.append(
                {
                    "Question": f"Please provide the ICH Q14 analytical procedure development rationale for {row['Test item']} - {row['Q14 check']}.",
                    "Triggered by": f"Q14 method setup review: {row['Status']} / {row['Risk']} risk",
                    "Evidence needed": str(row["Evidence to request"]),
                    "CTD update": str(row["CTD update"]),
                    "Owner": "Analytical Development / CMC RA",
                }
            )
        q3d_reviews = q3d_scope_report_frame()
        for _, row in q3d_reviews[q3d_reviews["Gate"] == "Review"].head(10).iterrows():
            additions.append(
                {
                    "Question": f"Please provide ICH Q3D source risk assessment, PDE/MDD basis, and ICP validation raw data for {row['Element']}.",
                    "Triggered by": f"Q3D elemental impurity gate: {row['Gate']} / {row['ICH Q3D class']}",
                    "Evidence needed": f"PDE {row['Route PDE entered (ug/day)']} ug/day, permitted concentration {row['Permitted concentration (ug/g)']} ug/g, LOQ/target {row['LOQ / target (%)']}%, recovery {row['Spike recovery (%)']}%, precision RSD {row['Precision RSD (%)']}%",
                    "CTD update": "3.2.P.5.3 / 3.2.P.5.5 / 3.2.P.5.6",
                    "Owner": "Analytical / Toxicology / CMC RA",
                }
            )
        related_frame = related_pde_report_frame()
        target = related_frame[related_frame["Threshold"] == "Validation target"].iloc[0]
        additions.append(
            {
                "Question": "Please confirm the related-substance PDE/TDI or ICH Q3B threshold basis used for the validation reference concentration.",
                "Triggered by": f"Related substance validation target {target['Limit (%)']:.4f}% / {target['Method concentration (ug/mL)']:.4f} ug/mL",
                "Evidence needed": str(target["Basis"]),
                "CTD update": "3.2.P.5.5 / 3.2.P.5.6",
                "Owner": "Analytical / Toxicology / CMC RA",
            }
        )
        return pd.concat([rows, pd.DataFrame(additions)], ignore_index=True) if additions else rows

    def build_decision_packet(profile: dict[str, Any]) -> str:
        packet = original_build_decision_packet(profile)
        summary = app.markdown_table(summary_frame(), ["Test item", "Gate", "Review items", "Regulatory basis", "CTD update"])
        q14_reviews = q14_report_frame(include_gate=True)
        q14_md = app.markdown_table(
            q14_reviews,
            ["Test item", "Q14 check", "Status", "Risk", "Gate", "Problem signal", "Evidence to request", "CTD update"],
        )
        reviews = review_frame(include_gate=True)
        review_md = app.markdown_table(reviews[reviews["Gate"] == "Review"], ["Test item", "Item", "Result", "Unit", "Rule", "Lower", "Upper", "Note", "CTD update"])
        related_pde = related_pde_report_frame()
        related_pde_md = app.markdown_table(
            related_pde,
            ["Threshold", "Limit (%)", "Method concentration (ug/mL)", "Basis", "Gate"],
        )
        q3d_scope = q3d_scope_report_frame()
        q3d_scope_md = app.markdown_table(
            q3d_scope,
            [
                "Element",
                "ICH Q3D class",
                "Default scope",
                "Route PDE entered (ug/day)",
                "Permitted concentration (ug/g)",
                "Control threshold concentration (ug/g)",
                "LOQ / target (%)",
                "Calculated LOQ vs control threshold (ug/g)",
                "Spike recovery (%)",
                "Precision RSD (%)",
                "Gate",
                "Note",
            ],
        )
        extra = f"## ICH Q14 Analytical Procedure Development Check\n\n{q14_md}\n## Test-Specific Validation Summary\n\n{summary}\n### Related Substance PDE/TDI Basis\n\n{related_pde_md}\n### ICH Q3D Elemental Impurity Scope\n\n{q3d_scope_md}\n### Validation Items Needing Review\n\n{review_md}\n"
        return packet.replace("## Response Memo Seed", extra + "\n## Response Memo Seed")

    app.initialize_state = initialize_state
    app.render_validation = render_validation
    app.response_rows = response_rows
    app.build_decision_packet = build_decision_packet

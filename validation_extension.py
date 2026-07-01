from __future__ import annotations

from html import escape
from typing import Any

import pandas as pd
import streamlit as st


APP_BUILD = "q3d-elemental-24-review-2026-06-30"


ELEMENTAL_IMPURITY_ELEMENTS: list[dict[str, str]] = [
    {"Element": "As", "Class": "Class 1", "Scope": "Core 7", "Risk question": "Toxic element; evaluate all potential API, excipient, equipment, water, and container sources."},
    {"Element": "Cd", "Class": "Class 1", "Scope": "Core 7", "Risk question": "Toxic element; evaluate all potential API, excipient, equipment, water, and container sources."},
    {"Element": "Hg", "Class": "Class 1", "Scope": "Core 7", "Risk question": "Toxic element; evaluate all potential API, excipient, equipment, water, and container sources."},
    {"Element": "Pb", "Class": "Class 1", "Scope": "Core 7", "Risk question": "Toxic element; evaluate all potential API, excipient, equipment, water, and container sources."},
    {"Element": "Co", "Class": "Class 2A", "Scope": "Core 7", "Risk question": "Naturally occurring or process-related risk; usually included in broad Q3D screening."},
    {"Element": "Ni", "Class": "Class 2A", "Scope": "Core 7", "Risk question": "Catalyst, stainless steel, or excipient/source risk; usually included in broad Q3D screening."},
    {"Element": "V", "Class": "Class 2A", "Scope": "Core 7", "Risk question": "Naturally occurring or catalyst/source risk; usually included in broad Q3D screening."},
    {"Element": "Ag", "Class": "Class 2B", "Scope": "Full 24", "Risk question": "Assess if intentionally added, catalyst-related, or source-specific risk is present."},
    {"Element": "Au", "Class": "Class 2B", "Scope": "Full 24", "Risk question": "Assess if intentionally added, catalyst-related, or source-specific risk is present."},
    {"Element": "Ir", "Class": "Class 2B", "Scope": "Full 24", "Risk question": "Assess if intentionally added, catalyst-related, or source-specific risk is present."},
    {"Element": "Os", "Class": "Class 2B", "Scope": "Full 24", "Risk question": "Assess if intentionally added, catalyst-related, or source-specific risk is present."},
    {"Element": "Pd", "Class": "Class 2B", "Scope": "Full 24", "Risk question": "Assess if intentionally added, catalyst-related, or source-specific risk is present."},
    {"Element": "Pt", "Class": "Class 2B", "Scope": "Full 24", "Risk question": "Assess if intentionally added, catalyst-related, or source-specific risk is present."},
    {"Element": "Rh", "Class": "Class 2B", "Scope": "Full 24", "Risk question": "Assess if intentionally added, catalyst-related, or source-specific risk is present."},
    {"Element": "Ru", "Class": "Class 2B", "Scope": "Full 24", "Risk question": "Assess if intentionally added, catalyst-related, or source-specific risk is present."},
    {"Element": "Se", "Class": "Class 2B", "Scope": "Full 24", "Risk question": "Assess if intentionally added, catalyst-related, or source-specific risk is present."},
    {"Element": "Tl", "Class": "Class 2B", "Scope": "Full 24", "Risk question": "Assess if intentionally added, catalyst-related, or source-specific risk is present."},
    {"Element": "Ba", "Class": "Class 3", "Scope": "Full 24", "Risk question": "Lower oral toxicity class; evaluate route and formulation/source-specific risk."},
    {"Element": "Cr", "Class": "Class 3", "Scope": "Full 24", "Risk question": "Lower oral toxicity class; evaluate route and formulation/source-specific risk."},
    {"Element": "Cu", "Class": "Class 3", "Scope": "Full 24", "Risk question": "Lower oral toxicity class; evaluate route and formulation/source-specific risk."},
    {"Element": "Li", "Class": "Class 3", "Scope": "Full 24", "Risk question": "Lower oral toxicity class; evaluate route and formulation/source-specific risk."},
    {"Element": "Mo", "Class": "Class 3", "Scope": "Full 24", "Risk question": "Lower oral toxicity class; evaluate route and formulation/source-specific risk."},
    {"Element": "Sb", "Class": "Class 3", "Scope": "Full 24", "Risk question": "Lower oral toxicity class; evaluate route and formulation/source-specific risk."},
    {"Element": "Sn", "Class": "Class 3", "Scope": "Full 24", "Risk question": "Lower oral toxicity class; evaluate route and formulation/source-specific risk."},
]


def elemental_scope_frame(scope: str = "core7") -> pd.DataFrame:
    full_scope = scope == "full24"
    rows: list[dict[str, Any]] = []
    for item in ELEMENTAL_IMPURITY_ELEMENTS:
        include = full_scope or item["Scope"] == "Core 7"
        rows.append(
            {
                "Include": include,
                "Element": item["Element"],
                "ICH Q3D class": item["Class"],
                "Default scope": item["Scope"],
                "Source / risk question": item["Risk question"],
                "Route PDE entered (ug/day)": 0.0,
                "Control target / J-value note": "Enter route-specific PDE and product MDD basis",
                "LOQ / target (%)": 10.0 if include else 0.0,
                "Spike recovery (%)": 92.0 if include else 0.0,
                "Precision RSD (%)": 12.0 if include else 0.0,
                "Note": "Q3D risk assessment + method validation raw data required" if include else "Add if product/source risk applies",
            }
        )
    return pd.DataFrame(rows)


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
    return f"{profile['en']} / {profile['ko']}" if lang == "en" else f"{profile['ko']} / {profile['en']}"


def _rows(profile: dict[str, Any]) -> pd.DataFrame:
    return pd.DataFrame(profile["rows"], columns=["Item", "Result", "Unit", "Rule", "Lower", "Upper", "Note"])


def _profile(key: str) -> dict[str, Any]:
    return next((profile for profile in PROFILES if profile["key"] == key), PROFILES[0])


def _ensure_tables() -> dict[str, pd.DataFrame]:
    if "validation_ext_tables" not in st.session_state:
        st.session_state.validation_ext_tables = {profile["key"]: _rows(profile) for profile in PROFILES}
    for profile in PROFILES:
        st.session_state.validation_ext_tables.setdefault(profile["key"], _rows(profile))
    return st.session_state.validation_ext_tables


def _element_gate(row: pd.Series) -> str:
    if not bool(row.get("Include", False)):
        return "N/A"
    loq_pct = pd.to_numeric(row.get("LOQ / target (%)"), errors="coerce")
    recovery = pd.to_numeric(row.get("Spike recovery (%)"), errors="coerce")
    rsd = pd.to_numeric(row.get("Precision RSD (%)"), errors="coerce")
    if pd.isna(loq_pct) or pd.isna(recovery) or pd.isna(rsd):
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
    app.TEXT["ko"]["calc_help"] = "함량, 유연물질, 용출, 금속불순물, 니트로사민별 시료 제조와 결과 gate를 검토합니다."
    app.TEXT["en"]["calc_help"] = "Review sample preparation and result gates by assay, related substances, dissolution, elemental impurities, and nitrosamines."

    original_initialize_state = app.initialize_state
    original_response_rows = app.response_rows
    original_build_decision_packet = app.build_decision_packet

    def initialize_state() -> None:
        original_initialize_state()
        st.session_state.setdefault("validation_test_item", "assay")
        _ensure_tables()

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

    def concentration_review(profile: dict[str, Any]) -> dict[str, Any]:
        ref, unit_default, level, weighed, purity, stock_volume, aliquot, final_volume, dilution = profile["prep"]
        prefix = f"ext_prep_{profile['key']}"
        st.caption(profile["focus"])
        c1, c2, c3 = st.columns(3)
        with c1:
            reference_conc = st.number_input("Reference concentration at 100%", min_value=0.000001, value=float(ref), step=0.1, format="%.6f", key=f"{prefix}_ref")
            unit = st.text_input("Concentration unit", value=str(unit_default), key=f"{prefix}_unit")
            level_pct = st.number_input("Validation level %", min_value=0.0, value=float(level), step=5.0, key=f"{prefix}_level")
        with c2:
            weighed_mg = st.number_input("Actual weighed amount (mg)", min_value=0.0, value=float(weighed), step=0.1, format="%.4f", key=f"{prefix}_weighed")
            purity_pct = st.number_input("Purity / potency correction %", min_value=0.0, value=float(purity), step=0.1, format="%.4f", key=f"{prefix}_purity")
            stock_volume_ml = st.number_input("Stock final volume (mL)", min_value=0.000001, value=float(stock_volume), step=10.0, format="%.4f", key=f"{prefix}_stock")
        with c3:
            aliquot_ml = st.number_input("Aliquot taken from stock (mL)", min_value=0.0, value=float(aliquot), step=0.1, format="%.4f", key=f"{prefix}_aliquot")
            final_volume_ml = st.number_input("Final volume after aliquot (mL)", min_value=0.000001, value=float(final_volume), step=10.0, format="%.4f", key=f"{prefix}_final")
            dilution_factor = st.number_input("Additional dilution factor", min_value=0.000001, value=float(dilution), step=0.5, format="%.4f", key=f"{prefix}_dilution")

        calc = app.calculate_sample_prep(reference_conc, level_pct, weighed_mg, purity_pct, stock_volume_ml, aliquot_ml, final_volume_ml, dilution_factor)
        metrics = st.columns(4)
        metrics[0].metric("Stock concentration", f"{float(calc['stock_conc']):.4f} {unit}")
        metrics[1].metric("Actual final concentration", f"{float(calc['final_conc']):.4f} {unit}")
        metrics[2].metric("Target concentration", f"{float(calc['target_conc']):.4f} {unit}")
        metrics[3].metric("Actual vs target", "N/A" if calc["diff_pct"] is None else f"{float(calc['diff_pct']):+.2f}%")
        if calc["gate"] == "Pass":
            st.success(str(calc["message"]))
        elif calc["gate"] == "Review":
            st.warning(str(calc["message"]))
        else:
            st.error(str(calc["message"]))
        return {"test_item": _label(profile, "en"), "reference_conc": reference_conc, "unit": unit, "final_conc": calc["final_conc"], "target_conc": calc["target_conc"], "diff_pct": calc["diff_pct"]}

    def lod_review(reference_conc: float, unit: str, profile: dict[str, Any]) -> list[str]:
        app.mini_heading("LOD / LOQ and intercept risk", "trend", "orange")
        lod, loq, r2, slope, intercept, response_100, response_loq, lowest = profile["lod"]
        prefix = f"ext_lod_{profile['key']}"
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            lod = st.number_input("LOD", min_value=0.0, value=float(lod), step=0.01, format="%.6f", key=f"{prefix}_lod")
            loq = st.number_input("LOQ", min_value=0.0, value=float(loq), step=0.01, format="%.6f", key=f"{prefix}_loq")
        with c2:
            r2 = st.number_input("Linearity R2", min_value=0.0, max_value=1.0, value=float(r2), step=0.0001, format="%.6f", key=f"{prefix}_r2")
            st.number_input("Mean slope", value=float(slope), step=100.0, format="%.4f", key=f"{prefix}_slope")
        with c3:
            intercept = st.number_input("Mean intercept", value=float(intercept), step=10.0, format="%.4f", key=f"{prefix}_intercept")
            response_100 = st.number_input("Response at 100%", min_value=0.000001, value=float(response_100), step=100.0, format="%.4f", key=f"{prefix}_r100")
        with c4:
            response_loq = st.number_input("Response at LOQ", min_value=0.000001, value=float(response_loq), step=50.0, format="%.4f", key=f"{prefix}_rloq")
            lowest = st.number_input("Lowest linearity level %", min_value=0.0, value=float(lowest), step=5.0, key=f"{prefix}_lowest")
        result = app.evaluate_lod_linearity(reference_conc, lod, loq, r2, intercept, response_100, response_loq, lowest)
        cols = st.columns(4)
        cols[0].metric("LOD / reference", f"{float(result['lod_pct']):.2f}%")
        cols[1].metric("LOQ / reference", f"{float(result['loq_pct']):.2f}%")
        cols[2].metric("Intercept / 100% response", f"{float(result['intercept_100_pct']):.2f}%")
        cols[3].metric("Intercept / LOQ response", f"{float(result['intercept_loq_pct']):.2f}%")
        notes = list(result["notes"])
        app.mini_heading(app.tr(st.session_state.lang, "risk_notes"), "alert", "orange")
        for note in notes:
            st.success(note) if "acceptable" in note else st.warning(note)
        return [f"{_label(profile, 'en')}: LOD {lod:.6f} {unit}", f"{_label(profile, 'en')}: LOQ {loq:.6f} {unit}", *notes]

    def render_elemental_scope_panel() -> None:
        app.mini_heading("ICH Q3D elemental impurity scope / 금속불순물 24종 범위", "atom", "green")
        mode = st.radio(
            "Q3D scope mode",
            ["Core 7: Class 1 + Class 2A", "Full Q3D 24 elements"],
            horizontal=True,
            key="q3d_scope_mode",
        )
        scope_key = "full24" if mode.startswith("Full") else "core7"
        previous_scope = st.session_state.get("q3d_scope_key")
        if previous_scope != scope_key or "q3d_element_df" not in st.session_state:
            st.session_state.q3d_scope_key = scope_key
            st.session_state.q3d_element_df = elemental_scope_frame(scope_key)

        element_df = st.session_state.q3d_element_df.copy()
        element_df["Gate"] = element_df.apply(_element_gate, axis=1)
        included = element_df[element_df["Include"]]
        class_counts = included["ICH Q3D class"].value_counts().to_dict()
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Included elements", f"{len(included)} / 24")
        c2.metric("Class 1", str(class_counts.get("Class 1", 0)))
        c3.metric("Class 2A", str(class_counts.get("Class 2A", 0)))
        c4.metric("Gate review", str(int((included["Gate"] == "Review").sum())))

        st.info(
            "Q3D practical read: Core 7 covers Class 1 (As, Cd, Hg, Pb) plus Class 2A "
            "(Co, Ni, V). Full Q3D screening expands to all 24 elements including Class 2B and Class 3."
        )
        edited_elements = st.data_editor(
            element_df.drop(columns=["Gate"], errors="ignore"),
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
        edited_elements["Gate"] = edited_elements.apply(_element_gate, axis=1)
        st.session_state.q3d_element_df = edited_elements.drop(columns=["Gate"], errors="ignore")

        active = edited_elements[edited_elements["Include"]]
        st.dataframe(
            active[
                [
                    "Element",
                    "ICH Q3D class",
                    "Default scope",
                    "LOQ / target (%)",
                    "Spike recovery (%)",
                    "Precision RSD (%)",
                    "Gate",
                    "Note",
                ]
            ],
            width="stretch",
            hide_index=True,
        )
        if scope_key == "core7" and len(active) < 7:
            st.warning("Core 7 mode should normally retain As, Cd, Hg, Pb, Co, Ni, and V unless a documented product risk rationale excludes an element.")
        if scope_key == "full24" and len(active) < 24:
            st.warning("Full Q3D 24 mode is selected, but not all 24 elements are included. Confirm the exclusion rationale.")

    def q3d_scope_report_frame() -> pd.DataFrame:
        if "q3d_element_df" not in st.session_state:
            return elemental_scope_frame("core7")
        frame = st.session_state.q3d_element_df.copy()
        frame["Gate"] = frame.apply(_element_gate, axis=1)
        return frame[frame["Include"]].copy()

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
        app.mini_heading("시험항목별 밸리데이션 선택 / Test-specific validation review", "shield", "orange")
        tables = _ensure_tables()
        current = st.session_state.get("validation_test_item", "assay")
        cards = []
        for profile in PROFILES:
            df = tables[profile["key"]].copy()
            df["Gate"] = df.apply(app.evaluate_rule, axis=1)
            review = int((df["Gate"] == "Review").sum())
            selected = " vcc-selected" if profile["key"] == current else ""
            cards.append(f'<article class="vcc-card{selected}" style="--tone:{profile["tone"]}"><span class="vcc-icon">{_svg(ICONS[profile["icon"]])}</span><strong>{escape(_label(profile, lang))}</strong><p>{escape(profile["purpose"])}</p><p>{review} review</p></article>')
        st.markdown(f'<div class="vcc-grid">{"".join(cards)}</div>', unsafe_allow_html=True)
        cols = st.columns(len(PROFILES))
        for idx, profile in enumerate(PROFILES):
            with cols[idx]:
                if st.button("Selected" if profile["key"] == current else "Open review", key=f"vcc_ext_{profile['key']}", use_container_width=True, type="primary" if profile["key"] == current else "secondary"):
                    st.session_state.validation_test_item = profile["key"]
                    st.rerun()

        profile = _profile(str(st.session_state.get("validation_test_item", "assay")))
        st.markdown(f'<div class="vcc-basis" style="--tone:{profile["tone"]}"><strong>{escape(_label(profile, lang))} review basis</strong><br><b>Regulatory basis:</b> {escape(profile["basis"])}<br><b>CTD location:</b> {escape(profile["ctd"])}<br><b>ICH M14 note:</b> {escape(profile["m14"])}</div>', unsafe_allow_html=True)
        if profile["key"] == "elemental_impurities":
            render_elemental_scope_panel()
        app.mini_heading(app.tr(lang, "sample_prep"), "calculator", "orange")
        calc = concentration_review(profile)
        notes = lod_review(float(calc["reference_conc"]), str(calc["unit"]), profile)
        app.mini_heading(app.tr(lang, "validation_gate"), "shield", "orange")
        st.info(f"Required result inputs for {_label(profile, lang)}: {'; '.join(str(item) for item in tables[profile['key']]['Item'].tolist())}")
        edited = st.data_editor(tables[profile["key"]], width="stretch", num_rows="dynamic", column_config={"Rule": st.column_config.SelectboxColumn("Rule", options=["between", "gte", "lte", "info"], required=True)}, key=f"vcc_ext_editor_{profile['key']}")
        edited = edited.copy().drop(columns=["Gate"], errors="ignore")
        edited["Gate"] = edited.apply(app.evaluate_rule, axis=1)
        tables[profile["key"]] = edited.drop(columns=["Gate"], errors="ignore")
        st.session_state.validation_ext_tables = tables
        st.dataframe(edited, width="stretch", hide_index=True)
        review_count = int((edited["Gate"] == "Review").sum())
        st.warning(f"{review_count} validation result item(s) need review before the Decision Packet is treated as ready.") if review_count else st.success("Validation result gate is passing for the selected test item.")
        app.mini_heading("시험항목별 전체 Gate 요약 / Overall validation item summary", "trend", "orange")
        st.dataframe(summary_frame(), width="stretch", hide_index=True)
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
        q3d_reviews = q3d_scope_report_frame()
        for _, row in q3d_reviews[q3d_reviews["Gate"] == "Review"].head(10).iterrows():
            additions.append(
                {
                    "Question": f"Please provide ICH Q3D source risk assessment, PDE/MDD basis, and ICP validation raw data for {row['Element']}.",
                    "Triggered by": f"Q3D elemental impurity gate: {row['Gate']} / {row['ICH Q3D class']}",
                    "Evidence needed": f"LOQ/target {row['LOQ / target (%)']}%, recovery {row['Spike recovery (%)']}%, precision RSD {row['Precision RSD (%)']}%",
                    "CTD update": "3.2.P.5.3 / 3.2.P.5.5 / 3.2.P.5.6",
                    "Owner": "Analytical / Toxicology / CMC RA",
                }
            )
        return pd.concat([rows, pd.DataFrame(additions)], ignore_index=True) if additions else rows

    def build_decision_packet(profile: dict[str, Any]) -> str:
        packet = original_build_decision_packet(profile)
        summary = app.markdown_table(summary_frame(), ["Test item", "Gate", "Review items", "Regulatory basis", "CTD update"])
        reviews = review_frame(include_gate=True)
        review_md = app.markdown_table(reviews[reviews["Gate"] == "Review"], ["Test item", "Item", "Result", "Unit", "Rule", "Lower", "Upper", "Note", "CTD update"])
        q3d_scope = q3d_scope_report_frame()
        q3d_scope_md = app.markdown_table(
            q3d_scope,
            ["Element", "ICH Q3D class", "Default scope", "LOQ / target (%)", "Spike recovery (%)", "Precision RSD (%)", "Gate", "Note"],
        )
        extra = f"## Test-Specific Validation Summary\n\n{summary}\n### ICH Q3D Elemental Impurity Scope\n\n{q3d_scope_md}\n### Validation Items Needing Review\n\n{review_md}\n"
        return packet.replace("## Response Memo Seed", extra + "\n## Response Memo Seed")

    app.initialize_state = initialize_state
    app.render_validation = render_validation
    app.response_rows = response_rows
    app.build_decision_packet = build_decision_packet

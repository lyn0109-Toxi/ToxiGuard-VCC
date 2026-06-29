from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st


APP_DIR = Path(__file__).resolve().parent
ASSET_DIR = APP_DIR / "assets"
PLATFORM_IMAGE = ASSET_DIR / "platform-home.png"


TEXT: dict[str, dict[str, str]] = {
    "ko": {
        "page_title": "ToxiGuard Platform Ver.3",
        "subtitle": "CMC RA Evidence Workbench",
        "positioning": "CTD 3.2.P 근거, 기준설정, DMF 연결성, 계산/밸리데이션, RA 답변 메모를 하나의 판단 흐름으로 묶는 Streamlit 작업대입니다.",
        "language": "Language / 언어",
        "product_profile": "제품 프로필",
        "dashboard": "Dashboard",
        "evidence_map": "01 Evidence Map",
        "spec_rationale": "02 P.5.6 Rationale",
        "dmf_bridge": "03 DMF Bridge",
        "validation": "04 Calculation / Validation",
        "response": "05 Response Memo",
        "launcher": "App Launcher",
        "readiness": "Evidence readiness",
        "open_risk": "Open high risks",
        "decision": "Decision gate",
        "core_modules": "5개 핵심 CMC RA 모듈",
        "module_help": "각 모듈은 최종 CMC RA Decision Packet의 근거 블록으로 연결됩니다.",
        "evidence_map_help": "P.1-P.8 자료 상태를 source, owner, risk, next action으로 관리합니다.",
        "spec_help": "품질기준이 비어 있거나 근거가 약하면 reviewer question으로 이어집니다.",
        "dmf_help": "원료 DMF 정보가 완제 CQA, 규격, 안정성, 불순물 전략을 지지하는지 확인합니다.",
        "calc_help": "실제 칭량량과 희석배수를 반영해 이론농도와 결과 gate를 검토합니다.",
        "response_help": "앞 단계의 gap을 보완질문, 필요한 근거, CTD 수정 위치로 바꿉니다.",
        "download": "Decision Packet 다운로드",
        "sample_prep": "샘플 제조 농도 검토",
        "validation_gate": "밸리데이션 결과 Gate",
        "risk_notes": "자동 Risk Notes",
        "available_apps": "현재 연결 가능한 앱",
        "next_builds": "다음 개발 앱",
    },
    "en": {
        "page_title": "ToxiGuard Platform Ver.3",
        "subtitle": "CMC RA Evidence Workbench",
        "positioning": "A Streamlit workbench that connects CTD 3.2.P evidence, specification rationale, DMF linkage, calculation/validation review, and CMC RA response writing.",
        "language": "Language",
        "product_profile": "Product Profile",
        "dashboard": "Dashboard",
        "evidence_map": "01 Evidence Map",
        "spec_rationale": "02 P.5.6 Rationale",
        "dmf_bridge": "03 DMF Bridge",
        "validation": "04 Calculation / Validation",
        "response": "05 Response Memo",
        "launcher": "App Launcher",
        "readiness": "Evidence readiness",
        "open_risk": "Open high risks",
        "decision": "Decision gate",
        "core_modules": "Five Core CMC RA Modules",
        "module_help": "Each module becomes an evidence block in the final CMC RA Decision Packet.",
        "evidence_map_help": "Manage P.1-P.8 evidence status by source, owner, risk, and next action.",
        "spec_help": "Missing criteria or weak rationale should become reviewer questions.",
        "dmf_help": "Check whether API DMF information supports DP CQA, specification, stability, and impurity strategy.",
        "calc_help": "Apply actual weighing and dilution factors to check theoretical concentration and result gates.",
        "response_help": "Convert gaps into deficiency questions, needed evidence, and CTD update locations.",
        "download": "Download Decision Packet",
        "sample_prep": "Sample Preparation Concentration Review",
        "validation_gate": "Validation Result Gate",
        "risk_notes": "Automatic Risk Notes",
        "available_apps": "Available Apps",
        "next_builds": "Next Builds",
    },
}


MODULES = [
    {
        "no": "1",
        "title": "3.2.P Evidence Map",
        "status": "Live in Ver.3",
        "output": "P.1-P.8 evidence map, gap list, reviewer question seed",
        "risk": "Missing source traceability or undefined CTD owner",
    },
    {
        "no": "2",
        "title": "P.5.6 Specification Rationale",
        "status": "Live in Ver.3",
        "output": "Specification rationale table and acceptance criteria memo",
        "risk": "Acceptance criterion without batch, stability, validation, or literature basis",
    },
    {
        "no": "3",
        "title": "DMF-to-DP Bridge",
        "status": "Live in Ver.3",
        "output": "API-to-drug-product bridge table and change impact note",
        "risk": "API potency, water, PSD, polymorph, impurity, or retest mismatch",
    },
    {
        "no": "4",
        "title": "Calculation / Validation Review",
        "status": "Live in Ver.3 + SOP Gate link",
        "output": "Sample prep concentration, dilution factor, LOD/LOQ %, intercept risk",
        "risk": "Reference concentration or dilution factor not reflected in validation level",
    },
    {
        "no": "5",
        "title": "CMC RA Response Memo",
        "status": "Live in Ver.3 draft",
        "output": "Response memo, required evidence, CTD update action table",
        "risk": "Answer draft not connected to source evidence or owner",
    },
]


STATUS_OPTIONS = ["Ready", "Partial", "Gap", "N/A"]
RISK_OPTIONS = ["Low", "Medium", "High"]
VALIDATION_STATUS = ["Validated", "Partial", "Not validated", "N/A"]


def default_evidence_rows() -> list[dict[str, Any]]:
    return [
        {
            "CTD section": "3.2.P.1 Description and Composition",
            "Core question": "Is product identity, composition, strength, route, and packaging clearly defined?",
            "Status": "Ready",
            "Source document": "Product composition table / batch formula",
            "Owner": "CMC RA",
            "Risk": "Low",
            "Next action": "Confirm latest formula and packaging version.",
        },
        {
            "CTD section": "3.2.P.2 Pharmaceutical Development",
            "Core question": "Does development rationale support QTPP, CQA, formulation, and process choices?",
            "Status": "Partial",
            "Source document": "Development report / comparative dissolution or IVR report",
            "Owner": "Formulation",
            "Risk": "Medium",
            "Next action": "Link CQA to specification and stability controls.",
        },
        {
            "CTD section": "3.2.P.3 Manufacture",
            "Core question": "Can the commercial process and IPC strategy consistently produce target quality?",
            "Status": "Partial",
            "Source document": "MFR / process flow / PV protocol",
            "Owner": "Manufacturing",
            "Risk": "Medium",
            "Next action": "Add CPP-CQA connection and process validation status.",
        },
        {
            "CTD section": "3.2.P.4 Control of Excipients",
            "Core question": "Are excipient standards, supplier controls, and novel excipient risks covered?",
            "Status": "Ready",
            "Source document": "Excipient COA / pharmacopeial standard",
            "Owner": "QC",
            "Risk": "Low",
            "Next action": "Confirm supplier qualification evidence.",
        },
        {
            "CTD section": "3.2.P.5 Control of Drug Product",
            "Core question": "Do specifications, methods, validation, and batch data support release and shelf-life quality?",
            "Status": "Gap",
            "Source document": "Specification / method validation / batch analysis",
            "Owner": "Analytical",
            "Risk": "High",
            "Next action": "Complete P.5.6 rationale and validation gate review.",
        },
        {
            "CTD section": "3.2.P.6 Reference Standards",
            "Core question": "Are reference standards qualified for assay, identity, and impurity testing?",
            "Status": "Partial",
            "Source document": "Reference standard COA / qualification report",
            "Owner": "QC",
            "Risk": "Medium",
            "Next action": "Confirm purity, water, storage, retest, and use history.",
        },
        {
            "CTD section": "3.2.P.7 Container Closure System",
            "Core question": "Does container closure evidence support compatibility, protection, and use?",
            "Status": "Partial",
            "Source document": "CCS specification / E&L / CCI",
            "Owner": "Packaging",
            "Risk": "Medium",
            "Next action": "Connect packaging evidence to P.2.4 and P.8 stability.",
        },
        {
            "CTD section": "3.2.P.8 Stability",
            "Core question": "Do stability data support proposed storage condition and shelf-life?",
            "Status": "Gap",
            "Source document": "Long-term / accelerated stability report",
            "Owner": "Stability",
            "Risk": "High",
            "Next action": "Add trend table, shelf-life justification, and commitment.",
        },
    ]


def default_spec_rows() -> list[dict[str, Any]]:
    return [
        {
            "Test item": "Assay",
            "Acceptance criterion": "95.0-105.0% of label claim",
            "Method": "HPLC assay",
            "Validation status": "Validated",
            "Rationale basis": "Batch data + method validation + stability trend",
            "Linked CQA": "Potency / dose delivery",
            "Risk": "Low",
            "Reviewer question": "Is assay basis aligned with API potency and water correction?",
        },
        {
            "Test item": "Related substances",
            "Acceptance criterion": "Individual impurity NMT 0.2%; total NMT 1.0%",
            "Method": "HPLC impurity method",
            "Validation status": "Partial",
            "Rationale basis": "ICH Q3B threshold + stability trend needed",
            "Linked CQA": "Safety / degradation control",
            "Risk": "High",
            "Reviewer question": "Are degradation products qualified and controlled through shelf-life?",
        },
        {
            "Test item": "Dissolution / IVR",
            "Acceptance criterion": "Profile matches target release window",
            "Method": "Dissolution or in vitro release",
            "Validation status": "Partial",
            "Rationale basis": "Development data + clinical/BE or reference bridge",
            "Linked CQA": "Performance / release rate",
            "Risk": "High",
            "Reviewer question": "Does the method discriminate formulation or process changes?",
        },
        {
            "Test item": "Particle size",
            "Acceptance criterion": "D10/D50/D90 within development range",
            "Method": "Laser diffraction",
            "Validation status": "Partial",
            "Rationale basis": "Development batches + manufacturability",
            "Linked CQA": "Release, syringeability, uniformity",
            "Risk": "Medium",
            "Reviewer question": "Is particle size linked to release profile and stability?",
        },
        {
            "Test item": "Residual solvent",
            "Acceptance criterion": "NMT ICH Q3C limit",
            "Method": "GC",
            "Validation status": "Validated",
            "Rationale basis": "ICH Q3C + process capability",
            "Linked CQA": "Safety",
            "Risk": "Low",
            "Reviewer question": "Is solvent removal controlled by process parameters?",
        },
        {
            "Test item": "Sterility / endotoxin",
            "Acceptance criterion": "Meets pharmacopeial requirement",
            "Method": "Sterility and BET",
            "Validation status": "Partial",
            "Rationale basis": "Aseptic process / terminal sterilization strategy",
            "Linked CQA": "Microbiological safety",
            "Risk": "High",
            "Reviewer question": "Is sterility assurance strategy supported by process validation?",
        },
    ]


def default_dmf_rows() -> list[dict[str, Any]]:
    return [
        {
            "DMF element": "Letter of authorization",
            "API / supplier evidence": "LoA available; DMF version to confirm",
            "DP impact": "Regulatory reference for API quality sections",
            "Applicant verification": "Partial",
            "Risk": "Medium",
            "Action": "Confirm current DMF version and holder commitment.",
        },
        {
            "DMF element": "API assay / potency basis",
            "API / supplier evidence": "COA assay value, water correction, potency statement",
            "DP impact": "Batch formula, assay calculation, label claim",
            "Applicant verification": "Partial",
            "Risk": "High",
            "Action": "Align potency correction with assay and sample prep calculation.",
        },
        {
            "DMF element": "Water content",
            "API / supplier evidence": "KF water range and batch COA",
            "DP impact": "Potency correction, stability, process moisture risk",
            "Applicant verification": "Partial",
            "Risk": "Medium",
            "Action": "Check water impact on actual theoretical value.",
        },
        {
            "DMF element": "Particle size distribution",
            "API / supplier evidence": "PSD method and supplier range",
            "DP impact": "Blend uniformity, dissolution/IVR, manufacturability",
            "Applicant verification": "Gap",
            "Risk": "High",
            "Action": "Bridge API PSD to DP CQA and method control.",
        },
        {
            "DMF element": "Impurity profile",
            "API / supplier evidence": "Specified/unspecified impurities, degradation risk",
            "DP impact": "Related substances specification and stability trend",
            "Applicant verification": "Gap",
            "Risk": "High",
            "Action": "Separate API impurity from DP degradant and qualify risk.",
        },
        {
            "DMF element": "Retest period / storage",
            "API / supplier evidence": "Retest period, storage condition, packaging",
            "DP impact": "Manufacturing hold time, stability commitment",
            "Applicant verification": "Partial",
            "Risk": "Medium",
            "Action": "Check whether API storage supports DP manufacturing timeline.",
        },
    ]


def default_validation_rows() -> list[dict[str, Any]]:
    return [
        {
            "Item": "Specificity recovery",
            "Result": 99.4,
            "Unit": "%",
            "Rule": "between",
            "Lower": 95.0,
            "Upper": 105.0,
            "Note": "Blank/placebo/API interference check",
        },
        {
            "Item": "Linearity R2",
            "Result": 0.9992,
            "Unit": "",
            "Rule": "gte",
            "Lower": 0.99,
            "Upper": None,
            "Note": "R2 alone is not enough if intercept risk is high",
        },
        {
            "Item": "Accuracy total recovery",
            "Result": 98.7,
            "Unit": "%",
            "Rule": "between",
            "Lower": 98.0,
            "Upper": 102.0,
            "Note": "Assay example; adjust per method profile",
        },
        {
            "Item": "Repeatability RSD",
            "Result": 1.4,
            "Unit": "%",
            "Rule": "lte",
            "Lower": None,
            "Upper": 2.0,
            "Note": "Six independent preparations",
        },
        {
            "Item": "Intermediate precision RSD",
            "Result": 2.3,
            "Unit": "%",
            "Rule": "lte",
            "Lower": None,
            "Upper": 2.0,
            "Note": "Different day / analyst / instrument",
        },
        {
            "Item": "Robustness RSD",
            "Result": 1.8,
            "Unit": "%",
            "Rule": "lte",
            "Lower": None,
            "Upper": 2.0,
            "Note": "Flow, wavelength, column lot, temperature, etc.",
        },
    ]


def initialize_state() -> None:
    defaults = {
        "evidence_df": pd.DataFrame(default_evidence_rows()),
        "spec_df": pd.DataFrame(default_spec_rows()),
        "dmf_df": pd.DataFrame(default_dmf_rows()),
        "validation_df": pd.DataFrame(default_validation_rows()),
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def tr(lang: str, key: str) -> str:
    return TEXT.get(lang, TEXT["ko"]).get(key, key)


def score_evidence(df: pd.DataFrame) -> float:
    weights = {"Ready": 1.0, "Partial": 0.55, "Gap": 0.0}
    applicable = df[df["Status"].isin(weights)]
    if applicable.empty:
        return 0.0
    return round(float(applicable["Status"].map(weights).mean() * 100), 1)


def count_high_risks(*frames: pd.DataFrame) -> int:
    total = 0
    for frame in frames:
        if "Risk" in frame.columns:
            total += int((frame["Risk"] == "High").sum())
    return total


def decision_gate(readiness: float, high_risk_count: int) -> tuple[str, str]:
    if readiness >= 80 and high_risk_count == 0:
        return "Go", "Evidence package is close to review-ready."
    if readiness >= 55 and high_risk_count <= 3:
        return "Watch", "Proceed with targeted gap closure before external use."
    return "Hold", "Resolve high-risk evidence gaps before relying on the package."


def evaluate_rule(row: pd.Series) -> str:
    result = pd.to_numeric(row.get("Result"), errors="coerce")
    lower = pd.to_numeric(row.get("Lower"), errors="coerce")
    upper = pd.to_numeric(row.get("Upper"), errors="coerce")
    rule = str(row.get("Rule", "")).strip().lower()
    if pd.isna(result) or rule in {"", "info", "nan"}:
        return "Info"
    if rule == "between":
        if pd.notna(lower) and result < lower:
            return "Review"
        if pd.notna(upper) and result > upper:
            return "Review"
        return "Pass"
    if rule == "gte":
        return "Pass" if pd.notna(lower) and result >= lower else "Review"
    if rule == "lte":
        return "Pass" if pd.notna(upper) and result <= upper else "Review"
    return "Info"


def risk_badge(label: str) -> None:
    if label == "Go":
        st.success(f"Decision gate: {label}")
    elif label == "Watch":
        st.warning(f"Decision gate: {label}")
    else:
        st.error(f"Decision gate: {label}")


def render_header(lang: str) -> None:
    left, right = st.columns([1.15, 0.85], vertical_alignment="center")
    with left:
        st.title(tr(lang, "page_title"))
        st.caption(tr(lang, "subtitle"))
        st.write(tr(lang, "positioning"))
    with right:
        if PLATFORM_IMAGE.exists():
            st.image(str(PLATFORM_IMAGE), width="stretch")


def render_sidebar(lang: str) -> dict[str, Any]:
    st.sidebar.header(tr(lang, "product_profile"))
    product = st.sidebar.text_input("Product", value="Naltrexone PLGA depot injection")
    dosage = st.sidebar.text_input("Dosage form", value="PLGA microsphere extended-release injection")
    strength = st.sidebar.text_input("Strength", value="380 mg/vial")
    route = st.sidebar.text_input("Route", value="Intramuscular")
    reference = st.sidebar.text_input("Reference / comparator", value="Vivitrol 380 mg or target reference")
    stage = st.sidebar.selectbox("Lifecycle stage", ["Development", "Validation", "Submission prep", "Response", "Lifecycle change"], index=2)
    st.sidebar.divider()
    st.sidebar.caption("GitHub target")
    st.sidebar.code("lyn0109-Toxi/ToxiGuard-VCC", language=None)
    return {
        "product": product,
        "dosage": dosage,
        "strength": strength,
        "route": route,
        "reference": reference,
        "stage": stage,
    }


def render_dashboard(lang: str, profile: dict[str, Any]) -> None:
    st.subheader(tr(lang, "core_modules"))
    st.write(tr(lang, "module_help"))
    module_cols = st.columns(5)
    for module, col in zip(MODULES, module_cols):
        with col:
            st.metric(f"{module['no']}. {module['title']}", module["status"])
            st.caption(module["output"])
            st.caption(f"Risk watch: {module['risk']}")

    readiness = score_evidence(st.session_state.evidence_df)
    high_risks = count_high_risks(st.session_state.evidence_df, st.session_state.spec_df, st.session_state.dmf_df)
    gate, gate_message = decision_gate(readiness, high_risks)
    m1, m2, m3 = st.columns(3)
    m1.metric(tr(lang, "readiness"), f"{readiness}%")
    m2.metric(tr(lang, "open_risk"), high_risks)
    m3.metric(tr(lang, "decision"), gate)
    risk_badge(gate)
    st.caption(gate_message)

    st.markdown("#### Decision context")
    st.dataframe(
        pd.DataFrame(
            [
                ["Product", profile["product"]],
                ["Dosage form", profile["dosage"]],
                ["Strength", profile["strength"]],
                ["Route", profile["route"]],
                ["Reference", profile["reference"]],
                ["Lifecycle stage", profile["stage"]],
            ],
            columns=["Field", "Value"],
        ),
        width="stretch",
        hide_index=True,
    )


def render_evidence_map(lang: str) -> None:
    st.subheader(tr(lang, "evidence_map"))
    st.write(tr(lang, "evidence_map_help"))
    st.session_state.evidence_df = st.data_editor(
        st.session_state.evidence_df,
        width="stretch",
        num_rows="dynamic",
        column_config={
            "Status": st.column_config.SelectboxColumn("Status", options=STATUS_OPTIONS, required=True),
            "Risk": st.column_config.SelectboxColumn("Risk", options=RISK_OPTIONS, required=True),
        },
        key="evidence_editor",
    )
    high = st.session_state.evidence_df[st.session_state.evidence_df["Risk"] == "High"]
    if not high.empty:
        st.warning("High-risk CTD sections need source-backed closure before the response memo is used.")
        st.dataframe(high[["CTD section", "Status", "Owner", "Next action"]], width="stretch", hide_index=True)


def render_spec_rationale(lang: str) -> None:
    st.subheader(tr(lang, "spec_rationale"))
    st.write(tr(lang, "spec_help"))
    st.session_state.spec_df = st.data_editor(
        st.session_state.spec_df,
        width="stretch",
        num_rows="dynamic",
        column_config={
            "Validation status": st.column_config.SelectboxColumn("Validation status", options=VALIDATION_STATUS, required=True),
            "Risk": st.column_config.SelectboxColumn("Risk", options=RISK_OPTIONS, required=True),
        },
        key="spec_editor",
    )
    weak = st.session_state.spec_df[
        (st.session_state.spec_df["Risk"] == "High")
        | (st.session_state.spec_df["Validation status"].isin(["Partial", "Not validated"]))
    ]
    st.markdown("#### Reviewer-risk focus")
    st.dataframe(
        weak[["Test item", "Acceptance criterion", "Validation status", "Risk", "Reviewer question"]],
        width="stretch",
        hide_index=True,
    )


def render_dmf_bridge(lang: str) -> None:
    st.subheader(tr(lang, "dmf_bridge"))
    st.write(tr(lang, "dmf_help"))
    st.session_state.dmf_df = st.data_editor(
        st.session_state.dmf_df,
        width="stretch",
        num_rows="dynamic",
        column_config={
            "Applicant verification": st.column_config.SelectboxColumn(
                "Applicant verification", options=["Verified", "Partial", "Gap", "N/A"], required=True
            ),
            "Risk": st.column_config.SelectboxColumn("Risk", options=RISK_OPTIONS, required=True),
        },
        key="dmf_editor",
    )
    high = st.session_state.dmf_df[st.session_state.dmf_df["Risk"] == "High"]
    if not high.empty:
        st.error("DMF-to-DP high-risk items should be closed before final CMC wording.")
        st.dataframe(high[["DMF element", "DP impact", "Action"]], width="stretch", hide_index=True)


def concentration_review() -> dict[str, float | str]:
    c1, c2, c3 = st.columns(3)
    with c1:
        reference_conc = st.number_input("Reference concentration at 100%", min_value=0.000001, value=2.5, step=0.1, format="%.6f")
        unit = st.text_input("Concentration unit", value="ug/mL")
        level_pct = st.number_input("Validation level %", min_value=0.0, value=100.0, step=5.0)
    with c2:
        weighed_mg = st.number_input("Actual weighed amount (mg)", min_value=0.0, value=25.0, step=0.1, format="%.4f")
        purity_pct = st.number_input("Purity / potency correction %", min_value=0.0, value=99.8, step=0.1, format="%.4f")
        stock_volume_ml = st.number_input("Stock final volume (mL)", min_value=0.000001, value=100.0, step=10.0, format="%.4f")
    with c3:
        aliquot_ml = st.number_input("Aliquot taken from stock (mL)", min_value=0.0, value=1.0, step=0.1, format="%.4f")
        final_volume_ml = st.number_input("Final volume after aliquot (mL)", min_value=0.000001, value=50.0, step=10.0, format="%.4f")
        dilution_factor = st.number_input("Additional dilution factor", min_value=0.000001, value=2.0, step=0.5, format="%.4f")

    stock_conc = weighed_mg * (purity_pct / 100.0) * 1000.0 / stock_volume_ml
    final_conc = stock_conc * aliquot_ml / final_volume_ml / dilution_factor
    target_conc = reference_conc * level_pct / 100.0
    diff_pct = ((final_conc - target_conc) / target_conc * 100.0) if target_conc else 0.0

    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Stock concentration", f"{stock_conc:.4f} {unit}")
    s2.metric("Actual final concentration", f"{final_conc:.4f} {unit}")
    s3.metric("Target concentration", f"{target_conc:.4f} {unit}")
    s4.metric("Actual vs target", f"{diff_pct:+.2f}%")

    if abs(diff_pct) <= 2:
        st.success("Sample prep gate: Pass. Actual theoretical concentration is close to target.")
    elif abs(diff_pct) <= 5:
        st.warning("Sample prep gate: Review. Check weighing, purity correction, volume, and dilution factor.")
    else:
        st.error("Sample prep gate: Hold. The prepared concentration does not support the target validation level.")

    return {
        "reference_conc": reference_conc,
        "unit": unit,
        "level_pct": level_pct,
        "stock_conc": stock_conc,
        "final_conc": final_conc,
        "target_conc": target_conc,
        "diff_pct": diff_pct,
    }


def linearity_and_lod_review(reference_conc: float, unit: str) -> list[str]:
    st.markdown("#### LOD / LOQ and intercept risk")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        lod = st.number_input("LOD", min_value=0.0, value=0.05, step=0.01, format="%.6f")
        loq = st.number_input("LOQ", min_value=0.0, value=0.15, step=0.01, format="%.6f")
    with c2:
        r2 = st.number_input("Linearity R2", min_value=0.0, max_value=1.0, value=0.9992, step=0.0001, format="%.6f")
        slope = st.number_input("Mean slope", value=12450.0, step=100.0, format="%.4f")
    with c3:
        intercept = st.number_input("Mean intercept", value=240.0, step=10.0, format="%.4f")
        response_100 = st.number_input("Response at 100%", min_value=0.000001, value=31125.0, step=100.0, format="%.4f")
    with c4:
        response_loq = st.number_input("Response at LOQ", min_value=0.000001, value=1867.5, step=50.0, format="%.4f")
        lowest_level_pct = st.number_input("Lowest linearity level %", min_value=0.0, value=20.0, step=5.0)

    lod_pct = lod / reference_conc * 100.0 if reference_conc else 0.0
    loq_pct = loq / reference_conc * 100.0 if reference_conc else 0.0
    intercept_100_pct = abs(intercept) / response_100 * 100.0
    intercept_loq_pct = abs(intercept) / response_loq * 100.0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("LOD / reference", f"{lod_pct:.2f}%")
    m2.metric("LOQ / reference", f"{loq_pct:.2f}%")
    m3.metric("Intercept / 100% response", f"{intercept_100_pct:.2f}%")
    m4.metric("Intercept / LOQ response", f"{intercept_loq_pct:.2f}%")

    notes: list[str] = []
    if r2 < 0.99:
        notes.append("Linearity R2 is below 0.99. Regression suitability is high risk.")
    if intercept_100_pct > 2.0:
        notes.append("Intercept is greater than 2% of the 100% response. Check blank, impurity/water contribution, and calibration range.")
    if intercept_loq_pct > 5.0:
        notes.append("Intercept is greater than 5% of the LOQ response. Low-level validation can be biased even when R2 is high.")
    if loq_pct > lowest_level_pct:
        notes.append("LOQ is higher than the lowest linearity level. Recheck range design.")
    if not notes:
        notes.append("LOD/LOQ and intercept risk are acceptable for the current reference concentration.")

    st.markdown("#### " + tr(st.session_state.lang, "risk_notes"))
    for note in notes:
        if "acceptable" in note:
            st.success(note)
        else:
            st.warning(note)

    return [f"LOD {lod:.6f} {unit} ({lod_pct:.2f}% of reference)", f"LOQ {loq:.6f} {unit} ({loq_pct:.2f}% of reference)", *notes]


def render_validation(lang: str) -> None:
    st.subheader(tr(lang, "validation"))
    st.write(tr(lang, "calc_help"))
    st.markdown("#### " + tr(lang, "sample_prep"))
    calc = concentration_review()
    risk_notes = linearity_and_lod_review(float(calc["reference_conc"]), str(calc["unit"]))

    st.markdown("#### " + tr(lang, "validation_gate"))
    edited = st.data_editor(
        st.session_state.validation_df,
        width="stretch",
        num_rows="dynamic",
        column_config={
            "Rule": st.column_config.SelectboxColumn("Rule", options=["between", "gte", "lte", "info"], required=True),
        },
        key="validation_editor",
    )
    edited = edited.copy()
    edited["Gate"] = edited.apply(evaluate_rule, axis=1)
    st.session_state.validation_df = edited.drop(columns=["Gate"], errors="ignore")
    st.dataframe(edited, width="stretch", hide_index=True)
    review_count = int((edited["Gate"] == "Review").sum())
    if review_count:
        st.warning(f"{review_count} validation result item(s) need review before the Decision Packet is treated as ready.")
    else:
        st.success("Validation result gate is passing for the current entries.")
    st.session_state["last_calc"] = calc
    st.session_state["last_risk_notes"] = risk_notes


def response_rows() -> pd.DataFrame:
    evidence = st.session_state.evidence_df
    spec = st.session_state.spec_df
    dmf = st.session_state.dmf_df
    rows: list[dict[str, str]] = []
    for _, row in evidence[evidence["Risk"] == "High"].iterrows():
        rows.append(
            {
                "Question": f"Please justify missing or incomplete evidence for {row['CTD section']}.",
                "Triggered by": row["Status"],
                "Evidence needed": row["Source document"],
                "CTD update": row["CTD section"],
                "Owner": row["Owner"],
            }
        )
    for _, row in spec[spec["Risk"] == "High"].iterrows():
        rows.append(
            {
                "Question": f"Please justify the acceptance criterion for {row['Test item']}.",
                "Triggered by": row["Reviewer question"],
                "Evidence needed": row["Rationale basis"],
                "CTD update": "3.2.P.5.6",
                "Owner": "Analytical / CMC RA",
            }
        )
    for _, row in dmf[dmf["Risk"] == "High"].iterrows():
        rows.append(
            {
                "Question": f"Please explain how {row['DMF element']} supports the drug product control strategy.",
                "Triggered by": row["DP impact"],
                "Evidence needed": row["API / supplier evidence"],
                "CTD update": "3.2.S / 3.2.P bridge",
                "Owner": "API / CMC RA",
            }
        )
    if not rows:
        rows.append(
            {
                "Question": "No high-risk response question is currently triggered.",
                "Triggered by": "Current evidence map",
                "Evidence needed": "Maintain source traceability",
                "CTD update": "N/A",
                "Owner": "CMC RA",
            }
        )
    return pd.DataFrame(rows)


def markdown_table(df: pd.DataFrame, columns: list[str]) -> str:
    if df.empty:
        return "No high-risk item currently listed.\n"

    def clean(value: Any) -> str:
        text = "" if pd.isna(value) else str(value)
        return text.replace("|", "\\|").replace("\n", "<br>")

    rows = df[columns].fillna("")
    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join(["---"] * len(columns)) + " |"
    body = ["| " + " | ".join(clean(row[col]) for col in columns) + " |" for _, row in rows.iterrows()]
    return "\n".join([header, separator, *body]) + "\n"


def build_decision_packet(profile: dict[str, Any]) -> str:
    evidence = st.session_state.evidence_df
    spec = st.session_state.spec_df
    dmf = st.session_state.dmf_df
    validation = st.session_state.validation_df.copy()
    validation["Gate"] = validation.apply(evaluate_rule, axis=1)
    readiness = score_evidence(evidence)
    high_risks = count_high_risks(evidence, spec, dmf)
    gate, message = decision_gate(readiness, high_risks)
    calc = st.session_state.get("last_calc", {})
    risk_notes = st.session_state.get("last_risk_notes", ["Run Calculation / Validation tab to generate LOD/LOQ and intercept notes."])

    high_evidence = evidence[evidence["Risk"] == "High"]
    high_spec = spec[spec["Risk"] == "High"]
    high_dmf = dmf[dmf["Risk"] == "High"]
    review_validation = validation[validation["Gate"] == "Review"]

    return f"""# ToxiGuard Platform Ver.3 CMC RA Decision Packet

Generated: {date.today().isoformat()}

## Product Context

| Field | Value |
| --- | --- |
| Product | {profile['product']} |
| Dosage form | {profile['dosage']} |
| Strength | {profile['strength']} |
| Route | {profile['route']} |
| Reference / comparator | {profile['reference']} |
| Lifecycle stage | {profile['stage']} |

## Decision Gate

- Gate: **{gate}**
- Evidence readiness: **{readiness}%**
- Open high risks: **{high_risks}**
- Interpretation: {message}

## High-Risk CTD Evidence

{markdown_table(high_evidence, ["CTD section", "Status", "Owner", "Next action"])}

## High-Risk Specification Rationale

{markdown_table(high_spec, ["Test item", "Acceptance criterion", "Rationale basis", "Reviewer question"])}

## High-Risk DMF-to-DP Bridge

{markdown_table(high_dmf, ["DMF element", "DP impact", "Action"])}

## Calculation / Validation Snapshot

- Reference concentration: {calc.get('reference_conc', 'Not run')} {calc.get('unit', '')}
- Actual final concentration: {calc.get('final_conc', 'Not run')} {calc.get('unit', '')}
- Target concentration: {calc.get('target_conc', 'Not run')} {calc.get('unit', '')}
- Actual vs target difference: {calc.get('diff_pct', 'Not run')}%

### LOD / LOQ / Intercept Notes

{chr(10).join(f"- {note}" for note in risk_notes)}

### Validation Items Needing Review

{markdown_table(review_validation, ["Item", "Result", "Unit", "Rule", "Lower", "Upper", "Note"])}

## Response Memo Seed

{markdown_table(response_rows(), ["Question", "Triggered by", "Evidence needed", "CTD update", "Owner"])}

## Expert Review Boundary

This packet is a decision-support draft. It does not replace CMC, analytical, regulatory, toxicology, clinical, legal, or quality expert review.
"""


def render_response(lang: str, profile: dict[str, Any]) -> None:
    st.subheader(tr(lang, "response"))
    st.write(tr(lang, "response_help"))
    rows = response_rows()
    st.dataframe(rows, width="stretch", hide_index=True)
    packet = build_decision_packet(profile)
    st.markdown("#### CMC RA Decision Packet Preview")
    st.text_area("Markdown preview", value=packet, height=360)
    st.download_button(
        tr(lang, "download"),
        data=packet,
        file_name="ToxiGuard_VCC_CMC_RA_Decision_Packet.md",
        mime="text/markdown",
    )


def render_launcher(lang: str) -> None:
    st.subheader(tr(lang, "launcher"))
    st.markdown("#### " + tr(lang, "available_apps"))
    available = pd.DataFrame(
        [
            {
                "App": "ToxiGuard-SOP Gate",
                "Role": "Calculation / Validation Review",
                "Run": "cd ../ToxiGuard-SOP-Gate && bash run_streamlit.sh",
            },
            {
                "App": "Clinical Trial Intelligence",
                "Role": "Clinical evidence layer",
                "Run": "python3 -m streamlit run ../clinical-trials-streamlit/app.py --server.port 8501",
            },
            {
                "App": "Revenue Forecast Intelligence",
                "Role": "Business evidence layer",
                "Run": "python3 -m streamlit run ../ToxiGuard-Revenue-Forecast/app.py --server.port 8511",
            },
        ]
    )
    st.dataframe(available, width="stretch", hide_index=True)
    st.markdown("#### " + tr(lang, "next_builds"))
    next_builds = pd.DataFrame(
        [
            ["Regulatory Framework Navigator", "ICH/FDA/EMA requirement to CTD evidence mapping"],
            ["Impurity Structure Insight Board", "Impurity origin, degradation route, ICH M7 rationale"],
            ["Stability Trend Evidence App", "Trend, shelf-life, OOS risk, commitment tracking"],
            ["CMC RA Response Memo Writer", "Full memo drafting with source crosswalk and action owners"],
        ],
        columns=["App", "Purpose"],
    )
    st.dataframe(next_builds, width="stretch", hide_index=True)


def main() -> None:
    st.set_page_config(
        page_title="ToxiGuard Platform Ver.3",
        page_icon="TG",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    initialize_state()
    with st.sidebar:
        lang_label = st.radio(tr("ko", "language"), ["한국어", "English"], horizontal=True)
        lang = "ko" if lang_label == "한국어" else "en"
        st.session_state.lang = lang
    profile = render_sidebar(st.session_state.lang)
    render_header(st.session_state.lang)

    tabs = st.tabs(
        [
            tr(st.session_state.lang, "dashboard"),
            tr(st.session_state.lang, "evidence_map"),
            tr(st.session_state.lang, "spec_rationale"),
            tr(st.session_state.lang, "dmf_bridge"),
            tr(st.session_state.lang, "validation"),
            tr(st.session_state.lang, "response"),
            tr(st.session_state.lang, "launcher"),
        ]
    )
    with tabs[0]:
        render_dashboard(st.session_state.lang, profile)
    with tabs[1]:
        render_evidence_map(st.session_state.lang)
    with tabs[2]:
        render_spec_rationale(st.session_state.lang)
    with tabs[3]:
        render_dmf_bridge(st.session_state.lang)
    with tabs[4]:
        render_validation(st.session_state.lang)
    with tabs[5]:
        render_response(st.session_state.lang, profile)
    with tabs[6]:
        render_launcher(st.session_state.lang)


if __name__ == "__main__":
    main()

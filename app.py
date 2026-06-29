from __future__ import annotations

import base64
from datetime import date
from html import escape
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
        "client_intake": "Client CTD Intake",
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
        "core_modules": "컨설턴트 CMC RA 워크플로우",
        "module_help": "고객 문서 접수부터 gap/risk 요약, 고객 질문 리스트, CTD 업데이트 방향까지 하나의 미팅 흐름으로 연결됩니다.",
        "client_intake_help": "고객이 제공한 DMF 기반 원료 정보, 완제 제조방법, 기준 및 시험방법 자료를 접수 품질과 CTD 업데이트 관점으로 정리합니다.",
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
        "meeting_summary": "고객 미팅 요약",
        "client_questions": "고객 질문 리스트",
        "ctd_update_direction": "CTD 업데이트 방향",
    },
    "en": {
        "page_title": "ToxiGuard Platform Ver.3",
        "subtitle": "CMC RA Evidence Workbench",
        "positioning": "A Streamlit workbench that connects CTD 3.2.P evidence, specification rationale, DMF linkage, calculation/validation review, and CMC RA response writing.",
        "language": "Language",
        "product_profile": "Product Profile",
        "client_intake": "Client CTD Intake",
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
        "core_modules": "Consultant CMC RA Workflow",
        "module_help": "Connect client document intake, gap/risk summary, client question list, and CTD update direction into one meeting flow.",
        "client_intake_help": "Capture the quality of client-provided DMF-based API information, drug product manufacturing, specification, and method documents against CTD update needs.",
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
        "meeting_summary": "Client Meeting Summary",
        "client_questions": "Client Question List",
        "ctd_update_direction": "CTD Update Direction",
    },
}


MODULES = [
    {
        "no": "0",
        "icon": "clipboard_check",
        "tone": "teal",
        "title": "Client CTD Intake",
        "status": "Live in Ver.3",
        "output": "Document received, intake quality, client questions, CTD update direction",
        "risk": "Client document is received but not traceable to DMF, DP process, specification, or CTD section",
    },
    {
        "no": "1",
        "icon": "network",
        "tone": "teal",
        "title": "3.2.P Evidence Map",
        "status": "Live in Ver.3",
        "output": "P.1-P.8 evidence map, gap list, reviewer question seed",
        "risk": "Missing source traceability or undefined CTD owner",
    },
    {
        "no": "2",
        "icon": "target",
        "tone": "amber",
        "title": "P.5.6 Specification Rationale",
        "status": "Live in Ver.3",
        "output": "Specification rationale table and acceptance criteria memo",
        "risk": "Acceptance criterion without batch, stability, validation, or literature basis",
    },
    {
        "no": "3",
        "icon": "bridge",
        "tone": "blue",
        "title": "DMF-to-DP Bridge",
        "status": "Live in Ver.3",
        "output": "API-to-drug-product bridge table and change impact note",
        "risk": "API potency, water, PSD, polymorph, impurity, or retest mismatch",
    },
    {
        "no": "4",
        "icon": "calculator",
        "tone": "orange",
        "title": "Calculation / Validation Review",
        "status": "Live in Ver.3 + SOP Gate link",
        "output": "Sample prep concentration, dilution factor, LOD/LOQ %, intercept risk",
        "risk": "Reference concentration or dilution factor not reflected in validation level",
    },
    {
        "no": "5",
        "icon": "file_pen",
        "tone": "green",
        "title": "CMC RA Response Memo",
        "status": "Live in Ver.3 draft",
        "output": "Response memo, required evidence, CTD update action table",
        "risk": "Answer draft not connected to source evidence or owner",
    },
]


NAV_ITEMS = [
    {
        "key": "intake",
        "label_key": "client_intake",
        "description": "Client document intake",
        "icon": "clipboard_check",
        "tone": "teal",
    },
    {
        "key": "dashboard",
        "label_key": "dashboard",
        "description": "Evidence overview",
        "icon": "gauge",
        "tone": "blue",
    },
    {
        "key": "evidence",
        "label_key": "evidence_map",
        "description": "CTD source map",
        "icon": "network",
        "tone": "teal",
    },
    {
        "key": "spec",
        "label_key": "spec_rationale",
        "description": "P.5.6 rationale",
        "icon": "target",
        "tone": "amber",
    },
    {
        "key": "dmf",
        "label_key": "dmf_bridge",
        "description": "API-to-DP bridge",
        "icon": "bridge",
        "tone": "blue",
    },
    {
        "key": "validation",
        "label_key": "validation",
        "description": "Concentration gate",
        "icon": "calculator",
        "tone": "orange",
    },
    {
        "key": "response",
        "label_key": "response",
        "description": "RA response memo",
        "icon": "file_pen",
        "tone": "green",
    },
    {
        "key": "launcher",
        "label_key": "launcher",
        "description": "Connected apps",
        "icon": "database",
        "tone": "blue",
    },
]


ICON_SVG = {
    "clipboard_check": '<rect x="6" y="4.2" width="12" height="17" rx="2"/><path d="M9 4.2a3 3 0 0 1 6 0"/><path d="M9 8h6"/><path d="m8.8 14 2 2 4.4-5"/><path d="M8.8 18h6.4"/>',
    "network": '<rect x="9" y="2.5" width="6" height="6" rx="1.2"/><rect x="2.5" y="15.5" width="6" height="6" rx="1.2"/><rect x="15.5" y="15.5" width="6" height="6" rx="1.2"/><path d="M12 8.5v4"/><path d="m5.5 15.5 6.5-3 6.5 3"/>',
    "target": '<circle cx="12" cy="12" r="8.5"/><circle cx="12" cy="12" r="4.8"/><circle cx="12" cy="12" r="1.5"/><path d="M12 2.5v3"/><path d="M21.5 12h-3"/><path d="M12 21.5v-3"/><path d="M2.5 12h3"/>',
    "bridge": '<path d="M3 17h18"/><path d="M5 17V9"/><path d="M19 17V9"/><path d="M7 17c.8-4.7 2.7-7 5-7s4.2 2.3 5 7"/><path d="M3 9h18"/><path d="M8 9v8"/><path d="M16 9v8"/>',
    "calculator": '<rect x="5" y="2.8" width="14" height="18.4" rx="2"/><path d="M8 6.5h8"/><path d="M8 10h.01"/><path d="M12 10h.01"/><path d="M16 10h.01"/><path d="M8 14h.01"/><path d="M12 14h.01"/><path d="M16 14h.01"/><path d="M8 18h.01"/><path d="M12 18h.01"/><path d="M16 18h.01"/>',
    "file_pen": '<path d="M14 2.8H7a2 2 0 0 0-2 2v14.4a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 2.8V8h5"/><path d="M8 13h4"/><path d="M8 17h2.5"/><path d="m13.5 17.5 4.6-4.6 1.4 1.4-4.6 4.6-2 .6z"/>',
    "gauge": '<path d="M4 15a8 8 0 1 1 16 0"/><path d="M12 15l4-5"/><path d="M4 19h16"/><path d="M7 15h.01"/><path d="M17 15h.01"/>',
    "alert": '<path d="m12 3 9 16H3z"/><path d="M12 8v5"/><path d="M12 17h.01"/>',
    "shield": '<path d="M12 2.8 19 6v5.5c0 4.2-2.8 7.9-7 9.7-4.2-1.8-7-5.5-7-9.7V6z"/><path d="m8.8 12.2 2.2 2.2 4.6-5"/>',
    "database": '<ellipse cx="12" cy="5" rx="7" ry="3"/><path d="M5 5v6c0 1.7 3.1 3 7 3s7-1.3 7-3V5"/><path d="M5 11v6c0 1.7 3.1 3 7 3s7-1.3 7-3v-6"/>',
    "trend": '<path d="M4 19h16"/><path d="M5 15l4-4 3 3 6-7"/><path d="M15 7h3v3"/>',
}


def svg_icon(name: str, class_name: str = "tg-icon") -> str:
    body = ICON_SVG.get(name, ICON_SVG["shield"])
    return (
        f'<svg class="{class_name}" viewBox="0 0 24 24" aria-hidden="true" '
        f'focusable="false" fill="none" stroke="currentColor" stroke-width="1.9" '
        f'stroke-linecap="round" stroke-linejoin="round">{body}</svg>'
    )


STATUS_OPTIONS = ["Ready", "Partial", "Gap", "N/A"]
RISK_OPTIONS = ["Low", "Medium", "High"]
VALIDATION_STATUS = ["Validated", "Partial", "Not validated", "N/A"]
INTAKE_RECEIVED_OPTIONS = ["Received", "Partial", "Missing", "N/A"]
INTAKE_QUALITY_OPTIONS = ["Usable", "Needs clarification", "Not usable", "N/A"]


def default_intake_rows() -> list[dict[str, Any]]:
    return [
        {
            "Intake area": "DMF authorization and version",
            "Expected client document": "LoA, DMF holder, DMF number/version, amendment history",
            "Received": "Partial",
            "Quality": "Needs clarification",
            "Risk": "High",
            "Consultant check": "Can the applicant reference the current DMF and confirm the version used for DP development?",
            "Client question": "Please provide the current LoA, DMF holder contact, and the DMF version/amendment basis used for this product.",
            "CTD update direction": "3.2.S reference / 3.2.P DMF bridge",
        },
        {
            "Intake area": "API potency, assay, and water basis",
            "Expected client document": "API COA, assay basis, KF/water, potency correction statement",
            "Received": "Partial",
            "Quality": "Needs clarification",
            "Risk": "High",
            "Consultant check": "Does API assay/water correction flow into batch formula, assay calculation, and validation reference concentration?",
            "Client question": "Please clarify whether the DP batch formula and analytical sample preparation use as-is, anhydrous, or potency-corrected API basis.",
            "CTD update direction": "3.2.P.3 formula / 3.2.P.5 assay calculation",
        },
        {
            "Intake area": "API impurity and degradant bridge",
            "Expected client document": "DMF impurity list, API COA trend, degradation pathway, qualification rationale",
            "Received": "Partial",
            "Quality": "Needs clarification",
            "Risk": "High",
            "Consultant check": "Are API impurities separated from DP degradants and controlled through shelf-life?",
            "Client question": "Please map API impurities and DP degradation products separately, including qualification and stability trend basis.",
            "CTD update direction": "3.2.P.5 related substances / 3.2.P.8 stability",
        },
        {
            "Intake area": "Drug product formula and manufacturing method",
            "Expected client document": "Master formula, batch formula, process flow, MFR, scale/batch size",
            "Received": "Partial",
            "Quality": "Needs clarification",
            "Risk": "High",
            "Consultant check": "Can the DP manufacturing method be traced from formula to CPP, IPC, CQA, and release specification?",
            "Client question": "Please provide the manufacturing flow with batch size, critical steps, IPCs, hold times, and CPP-CQA linkage.",
            "CTD update direction": "3.2.P.3 manufacture / 3.2.P.2 development",
        },
        {
            "Intake area": "Specification and test method package",
            "Expected client document": "DP specification, test methods, acceptance criteria, method version",
            "Received": "Received",
            "Quality": "Needs clarification",
            "Risk": "Medium",
            "Consultant check": "Are acceptance criteria justified by batch data, stability, validation, literature, or clinical/BE bridge?",
            "Client question": "Please identify the rationale source for each DP specification item and confirm method/version traceability.",
            "CTD update direction": "3.2.P.5.1 specification / 3.2.P.5.6 justification",
        },
        {
            "Intake area": "Analytical validation and batch results",
            "Expected client document": "Validation protocol/report, sample preparation, chromatograms, batch analysis",
            "Received": "Partial",
            "Quality": "Needs clarification",
            "Risk": "High",
            "Consultant check": "Do specificity, linearity, accuracy, precision, LOD/LOQ, and dilution factors support the stated validation levels?",
            "Client question": "Please provide method validation raw tables, sample preparation basis, dilution factors, and batch result linkage to specification.",
            "CTD update direction": "3.2.P.5.2 analytical procedures / 3.2.P.5.3 validation",
        },
        {
            "Intake area": "Stability and shelf-life support",
            "Expected client document": "Long-term/accelerated stability, trend table, storage condition, commitment",
            "Received": "Missing",
            "Quality": "Not usable",
            "Risk": "High",
            "Consultant check": "Can proposed shelf-life and storage condition be defended by trend and specification compliance?",
            "Client question": "Please provide stability tables, trend analysis, storage condition justification, and any post-approval commitment plan.",
            "CTD update direction": "3.2.P.8 stability",
        },
        {
            "Intake area": "Container closure and microbiological control",
            "Expected client document": "CCS specification, compatibility, CCI/E&L if applicable, sterility/endotoxin strategy",
            "Received": "Partial",
            "Quality": "Needs clarification",
            "Risk": "Medium",
            "Consultant check": "Does packaging and microbiological evidence support product protection, compatibility, and intended use?",
            "Client question": "Please provide container closure compatibility/protection evidence and microbiological control strategy.",
            "CTD update direction": "3.2.P.7 container closure / 3.2.P.5 microbiological tests",
        },
    ]


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
        "intake_df": pd.DataFrame(default_intake_rows()),
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


def score_intake(df: pd.DataFrame) -> float:
    if df.empty:
        return 0.0
    received_weights = {"Received": 1.0, "Partial": 0.55, "Missing": 0.0, "N/A": 0.7}
    quality_weights = {"Usable": 1.0, "Needs clarification": 0.5, "Not usable": 0.0, "N/A": 0.7}
    risk_weights = {"Low": 1.0, "Medium": 0.65, "High": 0.25}
    scores = []
    for _, row in df.iterrows():
        received = received_weights.get(str(row.get("Received", "")), 0.0)
        quality = quality_weights.get(str(row.get("Quality", "")), 0.0)
        risk = risk_weights.get(str(row.get("Risk", "")), 0.5)
        scores.append((received * 0.4) + (quality * 0.4) + (risk * 0.2))
    return round(float(sum(scores) / len(scores) * 100), 1)


def intake_focus_rows(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["Intake area", "Client question", "Expected client document", "Risk", "CTD update direction"])
    mask = (
        df["Risk"].eq("High")
        | df["Received"].isin(["Partial", "Missing"])
        | df["Quality"].isin(["Needs clarification", "Not usable"])
    )
    focus = df[mask].copy()
    if focus.empty:
        return pd.DataFrame(
            [
                {
                    "Intake area": "Current intake",
                    "Client question": "No major client question is currently triggered.",
                    "Expected client document": "Maintain source traceability",
                    "Risk": "Low",
                    "CTD update direction": "N/A",
                }
            ]
        )
    return focus[["Intake area", "Client question", "Expected client document", "Risk", "CTD update direction"]]


def intake_gap_count(df: pd.DataFrame) -> int:
    if df.empty:
        return 0
    return int(
        (
            df["Risk"].eq("High")
            | df["Received"].isin(["Partial", "Missing"])
            | df["Quality"].isin(["Needs clarification", "Not usable"])
        ).sum()
    )


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


def calculate_sample_prep(
    reference_conc: float,
    level_pct: float,
    weighed_mg: float,
    purity_pct: float,
    stock_volume_ml: float,
    aliquot_ml: float,
    final_volume_ml: float,
    dilution_factor: float,
) -> dict[str, float | str | None]:
    stock_conc = weighed_mg * (purity_pct / 100.0) * 1000.0 / stock_volume_ml
    final_conc = stock_conc * aliquot_ml / final_volume_ml / dilution_factor
    target_conc = reference_conc * level_pct / 100.0

    if target_conc <= 0:
        if abs(final_conc) <= 1e-12:
            return {
                "stock_conc": stock_conc,
                "final_conc": final_conc,
                "target_conc": target_conc,
                "diff_pct": 0.0,
                "gate": "Pass",
                "message": "Sample prep gate: Pass. Blank or zero-level preparation has no analyte concentration.",
            }
        return {
            "stock_conc": stock_conc,
            "final_conc": final_conc,
            "target_conc": target_conc,
            "diff_pct": None,
            "gate": "Hold",
            "message": "Sample prep gate: Hold. Target concentration is zero, but the prepared solution contains analyte.",
        }

    diff_pct = (final_conc - target_conc) / target_conc * 100.0
    if abs(diff_pct) <= 2:
        gate = "Pass"
        message = "Sample prep gate: Pass. Actual theoretical concentration is close to target."
    elif abs(diff_pct) <= 5:
        gate = "Review"
        message = "Sample prep gate: Review. Check weighing, purity correction, volume, and dilution factor."
    else:
        gate = "Hold"
        message = "Sample prep gate: Hold. The prepared concentration does not support the target validation level."

    return {
        "stock_conc": stock_conc,
        "final_conc": final_conc,
        "target_conc": target_conc,
        "diff_pct": diff_pct,
        "gate": gate,
        "message": message,
    }


def evaluate_lod_linearity(
    reference_conc: float,
    lod: float,
    loq: float,
    r2: float,
    intercept: float,
    response_100: float,
    response_loq: float,
    lowest_level_pct: float,
) -> dict[str, float | list[str]]:
    lod_pct = lod / reference_conc * 100.0
    loq_pct = loq / reference_conc * 100.0
    intercept_100_pct = abs(intercept) / response_100 * 100.0
    intercept_loq_pct = abs(intercept) / response_loq * 100.0

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

    return {
        "lod_pct": lod_pct,
        "loq_pct": loq_pct,
        "intercept_100_pct": intercept_100_pct,
        "intercept_loq_pct": intercept_loq_pct,
        "notes": notes,
    }


def risk_badge(label: str) -> None:
    if label == "Go":
        st.success(f"Decision gate: {label}")
    elif label == "Watch":
        st.warning(f"Decision gate: {label}")
    else:
        st.error(f"Decision gate: {label}")


@st.cache_data(show_spinner=False)
def platform_image_data_uri() -> str:
    if not PLATFORM_IMAGE.exists():
        return ""
    encoded = base64.b64encode(PLATFORM_IMAGE.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def entered_from_query() -> bool:
    value = st.query_params.get("enter", "")
    if isinstance(value, list):
        value = value[0] if value else ""
    return str(value).lower() in {"1", "true", "yes", "app", "workbench"}


def current_page_key() -> str:
    allowed = {str(item["key"]) for item in NAV_ITEMS}
    value = st.query_params.get("page", "intake")
    if isinstance(value, list):
        value = value[0] if value else "intake"
    page = str(value).lower()
    return page if page in allowed else "intake"


def should_show_landing() -> bool:
    if st.session_state.get("entered_app"):
        return False
    if entered_from_query():
        st.session_state.entered_app = True
        return False
    return True


def render_landing() -> None:
    image_src = platform_image_data_uri()
    image_markup = (
        f'<img src="{image_src}" alt="ToxiGuard Platform CMC RA Evidence Workbench" />'
        if image_src
        else '<div class="tg-fallback-title">ToxiGuard-VCC</div>'
    )
    st.markdown(
        f"""
        <style>
          [data-testid="stHeader"],
          [data-testid="stToolbar"],
          [data-testid="stDecoration"] {{
            display: none;
          }}
          .block-container {{
            max-width: 100%;
            padding: 0 !important;
          }}
          .tg-landing {{
            position: fixed;
            inset: 0;
            z-index: 9999;
            overflow: hidden;
            background: #071b3d;
          }}
          .tg-landing-link {{
            display: block;
            width: 100vw;
            height: 100vh;
            cursor: pointer;
            text-decoration: none;
          }}
          .tg-landing img {{
            width: 100vw;
            height: 100vh;
            object-fit: cover;
            object-position: center center;
            display: block;
          }}
          .tg-landing-link::after {{
            content: "";
            position: absolute;
            inset: 0;
            background:
              linear-gradient(180deg, rgba(7, 27, 61, 0.00) 48%, rgba(7, 27, 61, 0.38) 100%),
              radial-gradient(circle at 50% 86%, rgba(8, 127, 134, 0.28), rgba(7, 27, 61, 0.00) 34%);
            pointer-events: none;
          }}
          .tg-enter-panel {{
            position: absolute;
            left: 50%;
            bottom: clamp(24px, 6vh, 68px);
            transform: translateX(-50%);
            z-index: 2;
            width: min(520px, calc(100vw - 40px));
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 10px;
            text-align: center;
          }}
          .tg-enter-button {{
            min-height: 70px;
            width: min(360px, 100%);
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border: 2px solid rgba(255, 255, 255, 0.88);
            border-radius: 8px;
            padding: 14px 28px;
            color: #ffffff;
            background: rgba(7, 27, 61, 0.82);
            box-shadow: 0 18px 44px rgba(7, 27, 61, 0.38);
            font: 900 20px/1.15 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            backdrop-filter: blur(12px);
            transition: transform 160ms ease, background 160ms ease, border-color 160ms ease;
          }}
          .tg-enter-button::after {{
            content: ">";
            margin-left: 14px;
            font-size: 24px;
            line-height: 1;
          }}
          .tg-enter-note {{
            color: rgba(255, 255, 255, 0.9);
            background: rgba(7, 27, 61, 0.54);
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 999px;
            padding: 7px 13px;
            font: 750 13px/1.25 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            backdrop-filter: blur(8px);
          }}
          .tg-landing-link:hover .tg-enter-button,
          .tg-landing-link:focus-visible .tg-enter-button {{
            transform: translateY(-2px);
            background: rgba(8, 127, 134, 0.94);
            border-color: #ffffff;
          }}
          .tg-landing-link:focus-visible {{
            outline: 4px solid #89f1ee;
            outline-offset: -8px;
          }}
          .tg-fallback-title {{
            height: 100vh;
            display: grid;
            place-items: center;
            color: white;
            font: 800 48px/1.1 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
          }}
        </style>
        <div class="tg-landing">
          <a class="tg-landing-link" href="?enter=1" target="_self" aria-label="Enter ToxiGuard-VCC workbench">
            {image_markup}
            <span class="tg-enter-panel">
              <span class="tg-enter-button">Start Workbench</span>
              <span class="tg-enter-note">Click the image or this button to enter</span>
            </span>
          </a>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Enter Workbench", key="landing_enter_button", type="primary"):
        st.session_state.entered_app = True
        st.query_params["enter"] = "1"
        st.rerun()


def render_header(lang: str) -> None:
    image_src = platform_image_data_uri()
    background = (
        f'background-image: linear-gradient(90deg, rgba(7, 27, 61, 0.88), rgba(7, 27, 61, 0.55)), url("{image_src}");'
        if image_src
        else "background: #071b3d;"
    )
    hero_pills = "".join(
        f'<span class="tg-tone-{escape(module["tone"])}">{svg_icon(str(module["icon"]))}{escape(module["title"].replace(" Review", ""))}</span>'
        for module in MODULES
    )
    st.markdown(
        f"""
        <style>
          .main .block-container {{
            max-width: 1180px;
            padding-top: 28px;
          }}
          .tg-app-hero {{
            min-height: 250px;
            border-radius: 10px;
            overflow: hidden;
            background-size: cover;
            background-position: center center;
            box-shadow: 0 22px 52px rgba(7, 27, 61, 0.16);
            margin-bottom: 22px;
          }}
          .tg-app-hero-inner {{
            min-height: 250px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            padding: 34px 38px;
            color: #ffffff;
          }}
          .tg-eyebrow {{
            margin: 0 0 8px 0;
            color: #89f1ee;
            font-size: 0.78rem;
            font-weight: 800;
            text-transform: uppercase;
          }}
          .tg-app-hero h1 {{
            margin: 0 0 10px 0;
            font-size: 2.25rem;
            line-height: 1.08;
            letter-spacing: 0;
          }}
          .tg-app-hero p {{
            max-width: 680px;
            margin: 0;
            color: rgba(255, 255, 255, 0.9);
            font-size: 1rem;
            line-height: 1.55;
          }}
          .tg-icon {{
            width: 24px;
            height: 24px;
            flex: 0 0 auto;
          }}
          .tg-tone-teal {{
            --tg-accent: #087f86;
            --tg-accent-strong: #006068;
            --tg-accent-soft: #e2f4f2;
          }}
          .tg-tone-amber {{
            --tg-accent: #b57900;
            --tg-accent-strong: #735000;
            --tg-accent-soft: #fff2cf;
          }}
          .tg-tone-blue {{
            --tg-accent: #2867b2;
            --tg-accent-strong: #0b3d76;
            --tg-accent-soft: #e7f0fb;
          }}
          .tg-tone-orange {{
            --tg-accent: #c45b1d;
            --tg-accent-strong: #8b3710;
            --tg-accent-soft: #fde7dc;
          }}
          .tg-tone-green {{
            --tg-accent: #2f7d46;
            --tg-accent-strong: #1d5630;
            --tg-accent-soft: #e5f4e9;
          }}
          .tg-hero-pills {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 20px;
          }}
          .tg-hero-pills span,
          .tg-status-pill {{
            display: inline-flex;
            align-items: center;
            min-height: 28px;
            border-radius: 999px;
            padding: 5px 10px;
            font-size: 0.76rem;
            font-weight: 800;
          }}
          .tg-hero-pills span {{
            gap: 7px;
            border: 1px solid rgba(255, 255, 255, 0.36);
            color: #ffffff;
            background: rgba(255, 255, 255, 0.12);
            box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.16);
          }}
          .tg-hero-pills .tg-icon {{
            width: 17px;
            height: 17px;
          }}
          .tg-icon-nav {{
            display: grid;
            grid-template-columns: repeat(8, minmax(0, 1fr));
            gap: 8px;
            margin: -2px 0 22px;
            padding: 10px;
            border: 1px solid #dce6f0;
            border-radius: 8px;
            background: linear-gradient(180deg, #f8fbfd, #eef5f8);
            box-shadow: 0 14px 34px rgba(7, 27, 61, 0.07);
          }}
          .tg-nav-item {{
            min-height: 116px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: flex-start;
            gap: 8px;
            padding: 10px 8px 9px;
            border: 1px solid transparent;
            border-radius: 8px;
            background: #ffffff;
            color: #071b3d !important;
            text-decoration: none !important;
            text-align: center;
            position: relative;
            overflow: hidden;
            box-shadow: 0 6px 16px rgba(7, 27, 61, 0.05);
            transition: transform 160ms ease, box-shadow 160ms ease, border-color 160ms ease, background 160ms ease, color 160ms ease;
          }}
          .tg-nav-item::before {{
            content: "";
            position: absolute;
            inset: 0 0 auto;
            height: 4px;
            background: var(--tg-accent, #087f86);
            opacity: 0.88;
          }}
          .tg-nav-item:hover,
          .tg-nav-item:focus-visible {{
            transform: translateY(-2px);
            border-color: color-mix(in srgb, var(--tg-accent, #087f86) 58%, white);
            box-shadow: 0 16px 32px rgba(7, 27, 61, 0.12);
            outline: none;
          }}
          .tg-nav-item[aria-current="page"] {{
            background: linear-gradient(180deg, var(--tg-accent-soft, #e2f4f2), #ffffff 72%);
            border-color: color-mix(in srgb, var(--tg-accent, #087f86) 64%, white);
            box-shadow: 0 18px 36px rgba(7, 27, 61, 0.14);
          }}
          .tg-nav-icon {{
            display: inline-grid;
            place-items: center;
            width: 48px;
            height: 48px;
            flex: 0 0 48px;
            border-radius: 8px;
            color: var(--tg-accent-strong, #006068);
            background: var(--tg-accent-soft, #e2f4f2);
            border: 1px solid color-mix(in srgb, var(--tg-accent, #087f86) 30%, white);
            margin-top: 4px;
          }}
          .tg-nav-icon .tg-icon {{
            width: 27px;
            height: 27px;
          }}
          .tg-nav-item[aria-current="page"] .tg-nav-icon {{
            color: #ffffff;
            background: var(--tg-accent, #087f86);
            border-color: var(--tg-accent, #087f86);
          }}
          .tg-nav-copy {{
            display: block;
            width: 100%;
            min-width: 0;
          }}
          .tg-nav-label {{
            display: block;
            width: 100%;
            margin: 0;
            color: #071b3d;
            font-size: 0.82rem;
            font-weight: 900;
            line-height: 1.18;
            overflow-wrap: break-word;
            word-break: keep-all;
          }}
          .tg-nav-desc {{
            display: block;
            width: 100%;
            margin: 4px 0 0;
            color: #68758a;
            font-size: 0.68rem;
            font-weight: 750;
            line-height: 1.2;
            overflow: hidden;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
          }}
          .tg-nav-state {{
            position: absolute;
            right: 8px;
            top: 8px;
            min-height: 18px;
            display: none;
            align-items: center;
            border-radius: 999px;
            padding: 2px 7px;
            color: transparent;
            background: transparent;
            font-size: 0.62rem;
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: 0;
          }}
          .tg-nav-item[aria-current="page"] .tg-nav-state {{
            display: inline-flex;
            color: var(--tg-accent-strong, #006068);
            background: var(--tg-accent-soft, #e2f4f2);
          }}
          .tg-kpi-grid {{
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 12px;
            margin: 16px 0 26px;
          }}
          .tg-kpi-card,
          .tg-module-card {{
            border: 1px solid #d9e3ef;
            border-radius: 8px;
            background: #ffffff;
            box-shadow: 0 12px 30px rgba(7, 27, 61, 0.08);
          }}
          .tg-kpi-card {{
            padding: 16px 18px;
            position: relative;
            overflow: hidden;
            border-left: 5px solid var(--tg-accent, #087f86);
          }}
          .tg-kpi-card::after {{
            content: "";
            position: absolute;
            width: 96px;
            height: 96px;
            right: -32px;
            top: -42px;
            border-radius: 999px;
            background: var(--tg-accent-soft, #e2f4f2);
          }}
          .tg-kpi-head {{
            display: flex;
            align-items: center;
            gap: 10px;
            position: relative;
            z-index: 1;
          }}
          .tg-kpi-icon {{
            display: inline-grid;
            place-items: center;
            width: 42px;
            height: 42px;
            flex: 0 0 42px;
            border-radius: 8px;
            color: var(--tg-accent-strong, #006068);
            background: var(--tg-accent-soft, #e2f4f2);
            border: 1px solid color-mix(in srgb, var(--tg-accent, #087f86) 28%, white);
          }}
          .tg-kpi-icon .tg-icon {{
            width: 23px;
            height: 23px;
          }}
          .tg-kpi-label {{
            color: #68758a;
            font-size: 0.8rem;
            font-weight: 800;
            text-transform: uppercase;
          }}
          .tg-kpi-value {{
            margin-top: 4px;
            color: #071b3d;
            font-size: 1.85rem;
            font-weight: 900;
            line-height: 1.1;
            position: relative;
            z-index: 1;
          }}
          .tg-kpi-note {{
            margin-top: 6px;
            color: #5d6a7f;
            font-size: 0.88rem;
            position: relative;
            z-index: 1;
          }}
          .tg-section-title {{
            margin: 18px 0 10px;
            color: #071b3d;
            font-size: 1.35rem;
            font-weight: 900;
          }}
          .tg-flow-strip {{
            display: grid;
            grid-template-columns: repeat(5, minmax(0, 1fr));
            gap: 8px;
            margin: 8px 0 18px;
          }}
          .tg-flow-step {{
            min-height: 74px;
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 12px;
            border: 1px solid #d9e3ef;
            border-radius: 8px;
            background: #ffffff;
            box-shadow: 0 8px 20px rgba(7, 27, 61, 0.06);
          }}
          .tg-flow-step strong {{
            display: block;
            color: #071b3d;
            font-size: 0.84rem;
            line-height: 1.2;
          }}
          .tg-flow-step span {{
            color: #68758a;
            font-size: 0.72rem;
            font-weight: 750;
            line-height: 1.25;
          }}
          .tg-flow-index {{
            display: inline-grid;
            place-items: center;
            width: 34px;
            height: 34px;
            flex: 0 0 34px;
            border-radius: 8px;
            color: #ffffff;
            background: var(--tg-accent, #087f86);
            font-weight: 900;
          }}
          .tg-summary-box {{
            margin: 8px 0 16px;
            padding: 16px 18px;
            border: 1px solid #d9e3ef;
            border-left: 5px solid var(--tg-accent, #087f86);
            border-radius: 8px;
            background: linear-gradient(90deg, var(--tg-accent-soft, #e2f4f2), #ffffff 70%);
            color: #071b3d;
            line-height: 1.5;
          }}
          .tg-module-grid {{
            display: grid;
            grid-template-columns: repeat(5, minmax(0, 1fr));
            gap: 12px;
            margin-bottom: 24px;
          }}
          .tg-module-card {{
            min-height: 268px;
            padding: 16px;
            position: relative;
            overflow: hidden;
            border-top: 4px solid var(--tg-accent, #087f86);
            transition: transform 160ms ease, box-shadow 160ms ease, border-color 160ms ease;
          }}
          .tg-module-card::before {{
            content: "";
            position: absolute;
            inset: 0 0 auto 0;
            height: 84px;
            background: linear-gradient(180deg, var(--tg-accent-soft, #e2f4f2), rgba(255, 255, 255, 0));
            opacity: 0.82;
            pointer-events: none;
          }}
          .tg-module-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 18px 38px rgba(7, 27, 61, 0.13);
          }}
          .tg-module-top {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 10px;
            margin-bottom: 12px;
            position: relative;
            z-index: 1;
          }}
          .tg-module-identity {{
            display: flex;
            align-items: center;
            gap: 10px;
            min-width: 0;
          }}
          .tg-module-icon {{
            display: inline-grid;
            place-items: center;
            width: 54px;
            height: 54px;
            flex: 0 0 54px;
            border-radius: 8px;
            color: var(--tg-accent-strong, #006068);
            background: #ffffff;
            border: 1px solid color-mix(in srgb, var(--tg-accent, #087f86) 30%, white);
            box-shadow: 0 10px 24px rgba(7, 27, 61, 0.1);
          }}
          .tg-module-icon .tg-icon {{
            width: 29px;
            height: 29px;
          }}
          .tg-step {{
            display: inline-grid;
            place-items: center;
            width: 30px;
            height: 30px;
            border-radius: 999px;
            color: #ffffff;
            background: var(--tg-accent, #087f86);
            font-weight: 900;
            font-size: 0.86rem;
            box-shadow: 0 8px 16px color-mix(in srgb, var(--tg-accent, #087f86) 30%, transparent);
          }}
          .tg-status-pill {{
            color: var(--tg-accent-strong, #006068);
            background: var(--tg-accent-soft, #d9f2f0);
            border: 1px solid color-mix(in srgb, var(--tg-accent, #087f86) 26%, white);
          }}
          .tg-module-card h3 {{
            min-height: 52px;
            margin: 0 0 10px 0;
            color: #071b3d;
            font-size: 1rem;
            line-height: 1.25;
            position: relative;
            z-index: 1;
          }}
          .tg-module-card p {{
            margin: 0 0 12px 0;
            color: #4c5b70;
            font-size: 0.88rem;
            line-height: 1.45;
            position: relative;
            z-index: 1;
          }}
          .tg-risk {{
            border-top: 1px solid #e7eef6;
            padding-top: 10px;
            color: #735000;
            font-size: 0.8rem;
            line-height: 1.4;
            position: relative;
            z-index: 1;
          }}
          .tg-section-intro {{
            display: flex;
            align-items: center;
            gap: 14px;
            margin: 4px 0 18px;
            padding: 16px 18px;
            border: 1px solid #d9e3ef;
            border-left: 5px solid var(--tg-accent, #087f86);
            border-radius: 8px;
            background: linear-gradient(90deg, var(--tg-accent-soft, #e2f4f2), #ffffff 55%);
          }}
          .tg-section-icon {{
            display: inline-grid;
            place-items: center;
            width: 50px;
            height: 50px;
            flex: 0 0 50px;
            border-radius: 8px;
            color: var(--tg-accent-strong, #006068);
            background: #ffffff;
            border: 1px solid color-mix(in srgb, var(--tg-accent, #087f86) 28%, white);
            box-shadow: 0 10px 22px rgba(7, 27, 61, 0.08);
          }}
          .tg-section-icon .tg-icon {{
            width: 28px;
            height: 28px;
          }}
          .tg-section-copy h2 {{
            margin: 0 0 4px;
            color: #071b3d;
            font-size: 1.18rem;
            line-height: 1.22;
          }}
          .tg-section-copy p {{
            margin: 0;
            color: #4c5b70;
            line-height: 1.45;
          }}
          .tg-mini-heading {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            margin: 18px 0 8px;
            color: #071b3d;
            font-size: 1.02rem;
            font-weight: 900;
          }}
          .tg-mini-heading .tg-icon {{
            width: 20px;
            height: 20px;
            color: var(--tg-accent, #087f86);
          }}
          .tg-launcher-grid {{
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 12px;
            margin: 10px 0 18px;
          }}
          .tg-launcher-card {{
            border: 1px solid #d9e3ef;
            border-top: 4px solid var(--tg-accent, #087f86);
            border-radius: 8px;
            padding: 15px;
            background: #ffffff;
            box-shadow: 0 12px 30px rgba(7, 27, 61, 0.07);
          }}
          .tg-launcher-card h3 {{
            margin: 10px 0 6px;
            color: #071b3d;
            font-size: 1rem;
            line-height: 1.25;
          }}
          .tg-launcher-card p {{
            margin: 0;
            color: #4c5b70;
            font-size: 0.88rem;
            line-height: 1.4;
          }}
          .tg-context-table {{
            margin-top: 10px;
          }}
          [data-testid="collapsedControl"] button,
          [data-testid="stSidebarCollapseButton"] button,
          [data-testid="stSidebarCollapsedControl"] button {{
            min-width: 44px !important;
            min-height: 44px !important;
            border-radius: 8px !important;
            border: 1px solid #bddfdf !important;
            background: #f2fbfa !important;
            color: #006068 !important;
            box-shadow: 0 8px 18px rgba(7, 27, 61, 0.1) !important;
          }}
          @media (max-width: 1000px) {{
            .tg-icon-nav {{
              grid-template-columns: repeat(3, minmax(0, 1fr));
            }}
            .tg-module-grid {{
              grid-template-columns: repeat(2, minmax(0, 1fr));
            }}
            .tg-kpi-grid {{
              grid-template-columns: 1fr;
            }}
            .tg-launcher-grid {{
              grid-template-columns: 1fr;
            }}
            .tg-flow-strip {{
              grid-template-columns: 1fr;
            }}
          }}
          @media (max-width: 640px) {{
            .tg-app-hero-inner {{
              padding: 26px 22px;
            }}
            .tg-app-hero h1 {{
              font-size: 1.75rem;
            }}
            .tg-module-grid {{
              grid-template-columns: 1fr;
            }}
            .tg-icon-nav {{
              display: flex;
              overflow-x: auto;
              overflow-y: hidden;
              gap: 8px;
              padding: 8px;
              scroll-snap-type: x mandatory;
              -webkit-overflow-scrolling: touch;
            }}
            .tg-nav-item {{
              flex: 0 0 132px;
              min-height: 112px;
              padding: 10px 8px 8px;
              scroll-snap-align: start;
            }}
            .tg-nav-icon {{
              width: 44px;
              height: 44px;
              flex-basis: 44px;
            }}
            .tg-nav-icon .tg-icon {{
              width: 25px;
              height: 25px;
            }}
            .tg-nav-label {{
              font-size: 0.8rem;
            }}
            .tg-nav-desc {{
              display: none;
              font-size: 0.66rem;
              -webkit-line-clamp: 1;
            }}
            .tg-section-intro {{
              align-items: flex-start;
              padding: 14px;
            }}
            .tg-section-icon {{
              width: 44px;
              height: 44px;
              flex-basis: 44px;
            }}
          }}
        </style>
        <section class="tg-app-hero" style='{background}'>
          <div class="tg-app-hero-inner">
            <div class="tg-eyebrow">{escape(tr(lang, "subtitle"))}</div>
            <h1>ToxiGuard-VCC</h1>
            <p>{escape(tr(lang, "positioning"))}</p>
            <div class="tg-hero-pills">
              {hero_pills}
            </div>
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


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


def section_header(title: str, help_text: str, icon: str, tone: str) -> None:
    st.markdown(
        f"""
        <section class="tg-section-intro tg-tone-{escape(tone)}">
          <span class="tg-section-icon">{svg_icon(icon)}</span>
          <div class="tg-section-copy">
            <h2>{escape(title)}</h2>
            <p>{escape(help_text)}</p>
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def mini_heading(title: str, icon: str, tone: str) -> None:
    st.markdown(
        f'<div class="tg-mini-heading tg-tone-{escape(tone)}">{svg_icon(icon)}<span>{escape(title)}</span></div>',
        unsafe_allow_html=True,
    )


def render_icon_nav(lang: str, current_page: str) -> None:
    items = []
    for item in NAV_ITEMS:
        key = str(item["key"])
        label = tr(lang, str(item["label_key"]))
        is_active = key == current_page
        active_attr = ' aria-current="page"' if is_active else ""
        state_markup = '<span class="tg-nav-state">Selected</span>' if is_active else '<span class="tg-nav-state" aria-hidden="true"></span>'
        items.append(
            f'<a class="tg-nav-item tg-tone-{escape(str(item["tone"]))}" href="?enter=1&page={escape(key)}" '
            f'target="_self" aria-label="{escape(label)}"{active_attr}>'
            f'<span class="tg-nav-icon">{svg_icon(str(item["icon"]))}</span>'
            f'<span class="tg-nav-copy">'
            f'<span class="tg-nav-label">{escape(label)}</span>'
            f'<span class="tg-nav-desc">{escape(str(item["description"]))}</span>'
            f'</span>'
            f'{state_markup}'
            f'</a>'
        )
    st.markdown(f'<nav class="tg-icon-nav" aria-label="ToxiGuard module menu">{"".join(items)}</nav>', unsafe_allow_html=True)


def build_meeting_summary(profile: dict[str, Any]) -> str:
    intake = st.session_state.intake_df
    readiness = score_intake(intake)
    question_count = intake_gap_count(intake)
    high_count = int((intake["Risk"] == "High").sum()) if not intake.empty else 0
    focus = intake_focus_rows(intake)
    top_area = str(focus.iloc[0]["Intake area"]) if not focus.empty else "Current intake"
    top_question = str(focus.iloc[0]["Client question"]) if not focus.empty else "No major client question is currently triggered."
    top_update = str(focus.iloc[0]["CTD update direction"]) if not focus.empty else "N/A"
    return (
        f"Product: {profile['product']}\n"
        f"Meeting purpose: convert received client documents into gap/risk summary, client questions, and CTD update direction.\n"
        f"Intake readiness: {readiness}%\n"
        f"Open client questions: {question_count}\n"
        f"High-risk intake areas: {high_count}\n"
        f"First discussion focus: {top_area}\n"
        f"Priority client question: {top_question}\n"
        f"Likely CTD update direction: {top_update}"
    )


def render_intake_flow() -> None:
    steps = [
        ("1", "Document received", "DMF / DP / method package"),
        ("2", "Input", "status, quality, risk"),
        ("3", "Gap / risk summary", "meeting-ready view"),
        ("4", "Client questions", "evidence request list"),
        ("5", "CTD direction", "update target section"),
    ]
    st.markdown(
        '<div class="tg-flow-strip tg-tone-teal">'
        + "".join(
            f'<div class="tg-flow-step"><div class="tg-flow-index">{escape(no)}</div>'
            f'<div><strong>{escape(title)}</strong><span>{escape(note)}</span></div></div>'
            for no, title, note in steps
        )
        + "</div>",
        unsafe_allow_html=True,
    )


def render_client_intake(lang: str, profile: dict[str, Any]) -> None:
    section_header(tr(lang, "client_intake"), tr(lang, "client_intake_help"), "clipboard_check", "teal")
    render_intake_flow()

    st.session_state.intake_df = st.data_editor(
        st.session_state.intake_df,
        width="stretch",
        num_rows="dynamic",
        column_config={
            "Received": st.column_config.SelectboxColumn("Received", options=INTAKE_RECEIVED_OPTIONS, required=True),
            "Quality": st.column_config.SelectboxColumn("Quality", options=INTAKE_QUALITY_OPTIONS, required=True),
            "Risk": st.column_config.SelectboxColumn("Risk", options=RISK_OPTIONS, required=True),
        },
        key="intake_editor",
    )

    intake = st.session_state.intake_df
    readiness = score_intake(intake)
    question_count = intake_gap_count(intake)
    high_count = int((intake["Risk"] == "High").sum()) if not intake.empty else 0
    missing_count = int((intake["Received"] == "Missing").sum()) if not intake.empty else 0

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Intake readiness", f"{readiness}%")
    k2.metric("Client questions", question_count)
    k3.metric("High-risk areas", high_count)
    k4.metric("Missing documents", missing_count)

    summary = build_meeting_summary(profile)
    mini_heading(tr(lang, "meeting_summary"), "clipboard_check", "teal")
    st.markdown(
        f'<div class="tg-summary-box tg-tone-teal">{escape(summary).replace(chr(10), "<br>")}</div>',
        unsafe_allow_html=True,
    )

    focus = intake_focus_rows(intake)
    mini_heading(tr(lang, "client_questions"), "alert", "orange")
    st.dataframe(
        focus[["Intake area", "Client question", "Expected client document", "Risk"]],
        width="stretch",
        hide_index=True,
    )

    mini_heading(tr(lang, "ctd_update_direction"), "file_pen", "blue")
    st.dataframe(
        focus[["Intake area", "CTD update direction", "Risk"]],
        width="stretch",
        hide_index=True,
    )


def render_selected_page(page_key: str, lang: str, profile: dict[str, Any]) -> None:
    if page_key == "intake":
        render_client_intake(lang, profile)
    elif page_key == "evidence":
        render_evidence_map(lang)
    elif page_key == "spec":
        render_spec_rationale(lang)
    elif page_key == "dmf":
        render_dmf_bridge(lang)
    elif page_key == "validation":
        render_validation(lang)
    elif page_key == "response":
        render_response(lang, profile)
    elif page_key == "launcher":
        render_launcher(lang)
    else:
        render_dashboard(lang, profile)


def render_dashboard(lang: str, profile: dict[str, Any]) -> None:
    intake_readiness = score_intake(st.session_state.intake_df)
    readiness = score_evidence(st.session_state.evidence_df)
    high_risks = count_high_risks(
        st.session_state.intake_df,
        st.session_state.evidence_df,
        st.session_state.spec_df,
        st.session_state.dmf_df,
    )
    gate, gate_message = decision_gate(readiness, high_risks)
    kpi_markup = f"""
    <div class="tg-kpi-grid">
      <div class="tg-kpi-card tg-tone-teal">
        <div class="tg-kpi-head">
          <span class="tg-kpi-icon">{svg_icon("clipboard_check")}</span>
          <div class="tg-kpi-label">Intake readiness</div>
        </div>
        <div class="tg-kpi-value">{intake_readiness}%</div>
        <div class="tg-kpi-note">Client document usability</div>
      </div>
      <div class="tg-kpi-card tg-tone-teal">
        <div class="tg-kpi-head">
          <span class="tg-kpi-icon">{svg_icon("gauge")}</span>
          <div class="tg-kpi-label">{escape(tr(lang, "readiness"))}</div>
        </div>
        <div class="tg-kpi-value">{readiness}%</div>
        <div class="tg-kpi-note">P.1-P.8 source readiness</div>
      </div>
      <div class="tg-kpi-card tg-tone-orange">
        <div class="tg-kpi-head">
          <span class="tg-kpi-icon">{svg_icon("alert")}</span>
          <div class="tg-kpi-label">Client questions</div>
        </div>
        <div class="tg-kpi-value">{intake_gap_count(st.session_state.intake_df)}</div>
        <div class="tg-kpi-note">Questions to ask in meeting</div>
      </div>
      <div class="tg-kpi-card tg-tone-blue">
        <div class="tg-kpi-head">
          <span class="tg-kpi-icon">{svg_icon("shield")}</span>
          <div class="tg-kpi-label">{escape(tr(lang, "decision"))}</div>
        </div>
        <div class="tg-kpi-value">{escape(gate)}</div>
        <div class="tg-kpi-note">{escape(gate_message)}</div>
      </div>
    </div>
    """
    st.markdown(kpi_markup, unsafe_allow_html=True)

    cards = []
    for module in MODULES:
        cards.append(
            f'<article class="tg-module-card tg-tone-{escape(str(module["tone"]))}">'
            f'<div class="tg-module-top">'
            f'<div class="tg-module-identity">'
            f'<span class="tg-module-icon">{svg_icon(str(module["icon"]))}</span>'
            f'<span class="tg-step">{escape(module["no"])}</span>'
            f'</div>'
            f'<span class="tg-status-pill">Live</span>'
            f'</div>'
            f'<h3>{escape(module["title"])}</h3>'
            f'<p>{escape(module["output"])}</p>'
            f'<div class="tg-risk"><strong>Risk watch</strong><br>{escape(module["risk"])}</div>'
            f'</article>'
        )
    st.markdown(
        f'<div class="tg-section-title">{escape(tr(lang, "core_modules"))}</div>'
        f'<div style="color:#4c5b70; margin-bottom: 14px;">{escape(tr(lang, "module_help"))}</div>'
        f'<div class="tg-module-grid">{"".join(cards)}</div>',
        unsafe_allow_html=True,
    )

    mini_heading("Decision context", "shield", "blue")
    st.dataframe(
        pd.DataFrame(
            [
                ["Product", profile["product"]],
                ["Dosage form", profile["dosage"]],
                ["Strength", profile["strength"]],
                ["Route", profile["route"]],
                ["Reference", profile["reference"]],
                ["Lifecycle stage", profile["stage"]],
                ["Client intake readiness", f"{intake_readiness}%"],
                ["Open client questions", intake_gap_count(st.session_state.intake_df)],
                ["Open high risks", high_risks],
            ],
            columns=["Field", "Value"],
        ),
        width="stretch",
        hide_index=True,
    )


def render_evidence_map(lang: str) -> None:
    section_header(tr(lang, "evidence_map"), tr(lang, "evidence_map_help"), "network", "teal")
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
    section_header(tr(lang, "spec_rationale"), tr(lang, "spec_help"), "target", "amber")
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
    mini_heading("Reviewer-risk focus", "alert", "amber")
    st.dataframe(
        weak[["Test item", "Acceptance criterion", "Validation status", "Risk", "Reviewer question"]],
        width="stretch",
        hide_index=True,
    )


def render_dmf_bridge(lang: str) -> None:
    section_header(tr(lang, "dmf_bridge"), tr(lang, "dmf_help"), "bridge", "blue")
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


def concentration_review() -> dict[str, float | str | None]:
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

    calc = calculate_sample_prep(
        reference_conc=reference_conc,
        level_pct=level_pct,
        weighed_mg=weighed_mg,
        purity_pct=purity_pct,
        stock_volume_ml=stock_volume_ml,
        aliquot_ml=aliquot_ml,
        final_volume_ml=final_volume_ml,
        dilution_factor=dilution_factor,
    )
    stock_conc = float(calc["stock_conc"])
    final_conc = float(calc["final_conc"])
    target_conc = float(calc["target_conc"])
    diff_pct = calc["diff_pct"]

    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Stock concentration", f"{stock_conc:.4f} {unit}")
    s2.metric("Actual final concentration", f"{final_conc:.4f} {unit}")
    s3.metric("Target concentration", f"{target_conc:.4f} {unit}")
    s4.metric("Actual vs target", "N/A" if diff_pct is None else f"{float(diff_pct):+.2f}%")

    if calc["gate"] == "Pass":
        st.success(str(calc["message"]))
    elif calc["gate"] == "Review":
        st.warning(str(calc["message"]))
    else:
        st.error(str(calc["message"]))

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
    mini_heading("LOD / LOQ and intercept risk", "trend", "orange")
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

    linearity = evaluate_lod_linearity(
        reference_conc=reference_conc,
        lod=lod,
        loq=loq,
        r2=r2,
        intercept=intercept,
        response_100=response_100,
        response_loq=response_loq,
        lowest_level_pct=lowest_level_pct,
    )
    lod_pct = float(linearity["lod_pct"])
    loq_pct = float(linearity["loq_pct"])
    intercept_100_pct = float(linearity["intercept_100_pct"])
    intercept_loq_pct = float(linearity["intercept_loq_pct"])

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("LOD / reference", f"{lod_pct:.2f}%")
    m2.metric("LOQ / reference", f"{loq_pct:.2f}%")
    m3.metric("Intercept / 100% response", f"{intercept_100_pct:.2f}%")
    m4.metric("Intercept / LOQ response", f"{intercept_loq_pct:.2f}%")

    notes = list(linearity["notes"])

    mini_heading(tr(st.session_state.lang, "risk_notes"), "alert", "orange")
    for note in notes:
        if "acceptable" in note:
            st.success(note)
        else:
            st.warning(note)

    return [f"LOD {lod:.6f} {unit} ({lod_pct:.2f}% of reference)", f"LOQ {loq:.6f} {unit} ({loq_pct:.2f}% of reference)", *notes]


def render_validation(lang: str) -> None:
    section_header(tr(lang, "validation"), tr(lang, "calc_help"), "calculator", "orange")
    mini_heading(tr(lang, "sample_prep"), "calculator", "orange")
    calc = concentration_review()
    risk_notes = linearity_and_lod_review(float(calc["reference_conc"]), str(calc["unit"]))

    mini_heading(tr(lang, "validation_gate"), "shield", "orange")
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
    intake = st.session_state.intake_df
    evidence = st.session_state.evidence_df
    spec = st.session_state.spec_df
    dmf = st.session_state.dmf_df
    rows: list[dict[str, str]] = []
    intake_focus = intake_focus_rows(intake)
    for _, row in intake_focus[intake_focus["Risk"].isin(["High", "Medium"])].iterrows():
        if str(row["Client question"]).startswith("No major"):
            continue
        rows.append(
            {
                "Question": row["Client question"],
                "Triggered by": f"Client intake: {row['Intake area']} / {row['Risk']} risk",
                "Evidence needed": row["Expected client document"],
                "CTD update": row["CTD update direction"],
                "Owner": "Client / CMC RA",
            }
        )
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


def format_report_number(value: Any, decimals: int = 4) -> str:
    if value in {None, "Not run"}:
        return "Not run" if value == "Not run" else "N/A"
    try:
        return f"{float(value):.{decimals}f}"
    except (TypeError, ValueError):
        return str(value)


def format_report_diff(value: Any) -> str:
    if value is None:
        return "N/A"
    if value == "Not run":
        return "Not run"
    try:
        return f"{float(value):+.2f}%"
    except (TypeError, ValueError):
        return str(value)


def build_decision_packet(profile: dict[str, Any]) -> str:
    intake = st.session_state.intake_df
    evidence = st.session_state.evidence_df
    spec = st.session_state.spec_df
    dmf = st.session_state.dmf_df
    validation = st.session_state.validation_df.copy()
    validation["Gate"] = validation.apply(evaluate_rule, axis=1)
    intake_readiness = score_intake(intake)
    readiness = score_evidence(evidence)
    high_risks = count_high_risks(intake, evidence, spec, dmf)
    gate, message = decision_gate(readiness, high_risks)
    calc = st.session_state.get("last_calc", {})
    risk_notes = st.session_state.get("last_risk_notes", ["Run Calculation / Validation tab to generate LOD/LOQ and intercept notes."])

    intake_focus = intake_focus_rows(intake)
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
- Client intake readiness: **{intake_readiness}%**
- Evidence readiness: **{readiness}%**
- Open high risks: **{high_risks}**
- Interpretation: {message}

## Client CTD Intake Snapshot

{markdown_table(intake_focus, ["Intake area", "Client question", "Expected client document", "Risk", "CTD update direction"])}

## High-Risk CTD Evidence

{markdown_table(high_evidence, ["CTD section", "Status", "Owner", "Next action"])}

## High-Risk Specification Rationale

{markdown_table(high_spec, ["Test item", "Acceptance criterion", "Rationale basis", "Reviewer question"])}

## High-Risk DMF-to-DP Bridge

{markdown_table(high_dmf, ["DMF element", "DP impact", "Action"])}

## Calculation / Validation Snapshot

- Reference concentration: {format_report_number(calc.get('reference_conc', 'Not run'))} {calc.get('unit', '')}
- Actual final concentration: {format_report_number(calc.get('final_conc', 'Not run'))} {calc.get('unit', '')}
- Target concentration: {format_report_number(calc.get('target_conc', 'Not run'))} {calc.get('unit', '')}
- Actual vs target difference: {format_report_diff(calc.get('diff_pct', 'Not run'))}

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
    section_header(tr(lang, "response"), tr(lang, "response_help"), "file_pen", "green")
    rows = response_rows()
    st.dataframe(rows, width="stretch", hide_index=True)
    packet = build_decision_packet(profile)
    mini_heading("CMC RA Decision Packet Preview", "file_pen", "green")
    st.text_area("Markdown preview", value=packet, height=360)
    st.download_button(
        tr(lang, "download"),
        data=packet,
        file_name="ToxiGuard_VCC_CMC_RA_Decision_Packet.md",
        mime="text/markdown",
    )


def render_launcher(lang: str) -> None:
    section_header(tr(lang, "launcher"), "Open connected ToxiGuard apps and plan the next evidence workbench modules.", "database", "blue")
    mini_heading(tr(lang, "available_apps"), "database", "blue")
    launcher_cards = [
        ("ToxiGuard-SOP Gate", "Calculation / Validation Review", "calculator", "orange"),
        ("Clinical Trial Intelligence", "Clinical evidence layer", "trend", "teal"),
        ("Revenue Forecast Intelligence", "Business evidence layer", "gauge", "green"),
    ]
    st.markdown(
        '<div class="tg-launcher-grid">'
        + "".join(
            f'<article class="tg-launcher-card tg-tone-{escape(tone)}">'
            f'<span class="tg-section-icon">{svg_icon(icon)}</span>'
            f'<h3>{escape(name)}</h3>'
            f'<p>{escape(role)}</p>'
            f'</article>'
            for name, role, icon, tone in launcher_cards
        )
        + "</div>",
        unsafe_allow_html=True,
    )
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
    mini_heading(tr(lang, "next_builds"), "trend", "blue")
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
        initial_sidebar_state="collapsed",
    )
    if should_show_landing():
        render_landing()
        return

    initialize_state()
    with st.sidebar:
        lang_label = st.radio(tr("ko", "language"), ["한국어", "English"], horizontal=True)
        lang = "ko" if lang_label == "한국어" else "en"
        st.session_state.lang = lang
    profile = render_sidebar(st.session_state.lang)
    render_header(st.session_state.lang)
    page_key = current_page_key()
    render_icon_nav(st.session_state.lang, page_key)
    render_selected_page(page_key, st.session_state.lang, profile)


if __name__ == "__main__":
    main()

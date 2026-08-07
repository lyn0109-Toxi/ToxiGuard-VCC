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
APP_BUILD = "validation-item-review-2026-06-30"


TEXT: dict[str, dict[str, str]] = {
    "ko": {
        "page_title": "ToxiGuard Platform Ver.3",
        "subtitle": "CMC RA Evidence Workbench",
        "positioning": "CTD 3.2.P 근거, 기준설정, DMF 연결성, 계산/밸리데이션, RA 답변 메모를 하나의 판단 흐름으로 묶는 Streamlit 작업대입니다.",
        "language": "Language / 언어",
        "product_profile": "제품 프로필",
        "client_intake": "고객 CTD 문서 접수",
        "document_workspace": "00 문서 입력",
        "dashboard": "대시보드",
        "evidence_map": "01 근거 맵",
        "spec_rationale": "02 P.5.6 기준 설정 근거",
        "dmf_bridge": "03 DMF-완제 연결성",
        "validation": "04 계산 / 밸리데이션",
        "response": "05 RA 답변 메모",
        "launcher": "앱 실행",
        "readiness": "Evidence readiness",
        "open_risk": "미해결 고위험",
        "decision": "판단 게이트",
        "core_modules": "컨설턴트 CMC RA 워크플로우",
        "module_help": "고객 문서 접수부터 gap/risk 요약, 고객 질문 리스트, CTD 업데이트 방향까지 하나의 미팅 흐름으로 연결됩니다.",
        "client_intake_help": "고객이 제공한 DMF 기반 원료 정보, 완제 제조방법, 기준 및 시험방법 자료를 접수 품질과 CTD 업데이트 관점으로 정리합니다.",
        "document_workspace_help": "제품 프로필에 맞춰 DMF 원문 정보, CTD 3.2.S, CTD 3.2.P, 기타 CTD 모듈의 실제 문서 입력값을 관리합니다.",
        "evidence_map_help": "P.1-P.8 자료 상태를 source, owner, risk, next action으로 관리합니다.",
        "spec_help": "품질기준이 비어 있거나 근거가 약하면 reviewer question으로 이어집니다.",
        "dmf_help": "원료 DMF 정보가 완제 CQA, 규격, 안정성, 불순물 전략을 지지하는지 확인합니다.",
        "calc_help": "함량, 유연물질, 용출, 금속불순물, 니트로사민별 시료 제조와 결과 gate를 검토합니다.",
        "response_help": "앞 단계의 gap을 보완질문, 필요한 근거, CTD 수정 위치로 바꿉니다.",
        "download": "Decision Packet 다운로드",
        "sample_prep": "시험항목별 샘플 제조 농도 검토",
        "validation_gate": "시험항목별 밸리데이션 결과 Gate",
        "risk_notes": "자동 Risk Notes",
        "available_apps": "현재 연결 가능한 앱",
        "next_builds": "다음 개발 앱",
        "meeting_summary": "고객 미팅 요약",
        "client_questions": "고객 질문 리스트",
        "ctd_update_direction": "CTD 업데이트 방향",
        "enter_workbench": "워크벤치 시작",
        "landing_enter_note": "이미지 또는 버튼을 클릭해 앱으로 이동",
        "selected": "선택됨",
        "open_review": "검토 열기",
        "live": "사용 가능",
        "risk_watch": "리스크 확인",
        "decision_context": "판단 배경",
        "intake_readiness": "문서 접수 준비도",
        "client_document_usability": "고객 문서 활용 가능성",
        "source_readiness": "3.2.S/P 근거 준비도",
        "ctd_document_readiness": "CTD 문서 준비도",
        "dmf_document_readiness": "DMF 문서 준비도",
        "source_text_entries": "입력된 원문 근거",
        "profile_driven_prompts": "제품 프로필 기반 검토 질문",
        "dmf_source_input": "DMF 원문 입력",
        "ctd_3_2_s_input": "CTD 3.2.S 원료의약품 입력",
        "ctd_3_2_p_input": "CTD 3.2.P 완제의약품 입력",
        "ctd_other_parts_input": "기타 CTD 모듈 입력",
        "ctd_module_strategy": "CTD 모듈 운영 전략",
        "document_input_strategy": "Module 3는 상세 CMC 근거로 관리하고, Module 1/2/4/5는 허가·임상·비임상 문맥과 CMC 변경 영향의 연결 근거로 관리합니다.",
        "company_document_flow": "회사 문서 적용 흐름",
        "document_logic": "문서 적용 로직",
        "document_logic_help": "실제 회사 문서를 CMC 판단 질문, CTD 반영 위치, 보완 action으로 바꾸는 운영 규칙입니다. 모든 행은 프로젝트에 맞게 수정할 수 있습니다.",
        "key_decision_points": "핵심 판단 포인트",
        "document_review_boundary": "앱은 문서의 결론을 대신 확정하지 않습니다. 원문과 확인값을 근거로 리스크 질문을 정렬하고, 최종 판단은 CMC RA 전문가가 수정·확정합니다.",
        "apply_document_inputs": "문서 입력값을 근거 맵에 적용",
        "apply_document_inputs_help": "현재 DMF/CTD 입력값을 3.2.S/P Evidence Map, DMF-to-DP Bridge, P.5.6 리스크 seed에 반영합니다.",
        "apply_document_inputs_done": "문서 입력값을 워크벤치에 반영했습니다.",
        "raw_document_paste": "긴 문서 발췌 / 원문 메모",
        "questions_to_ask": "미팅에서 확인할 질문",
        "product": "제품명",
        "active_substance": "원료의약품 / 주성분",
        "api_supplier": "API 공급처 / DMF holder",
        "formulation_platform": "제형 기술 / 플랫폼",
        "clinical_material": "임상시험용 의약품 / 배치",
        "target_regions": "대상 허가 지역",
        "dosage_form": "제형",
        "strength": "함량",
        "route": "투여경로",
        "reference": "대조/참조 제품",
        "lifecycle_stage": "개발 단계",
        "github_target": "GitHub 대상",
        "document_received": "문서 접수",
        "input": "입력",
        "gap_risk_summary": "Gap / Risk 요약",
        "ctd_direction": "CTD 방향",
        "meeting_ready_view": "미팅용 보기",
        "evidence_request_list": "근거 요청 리스트",
        "update_target_section": "수정 대상 CTD",
        "status": "상태",
        "risk": "리스크",
        "quality": "품질",
        "received": "수신 상태",
        "validation_select": "시험항목별 밸리데이션 선택",
        "validation_basis": "검토 기준",
        "regulatory_basis": "규제 근거",
        "ctd_location": "CTD 위치",
        "m14_note": "ICH M14 메모",
        "result_inputs": "필요 결과 입력값",
        "validation_review_warning": "Decision Packet을 준비 상태로 보기 전에 검토가 필요한 밸리데이션 결과 항목이 있습니다.",
        "validation_review_success": "선택한 시험항목의 밸리데이션 결과 Gate가 통과 상태입니다.",
        "overall_validation_summary": "시험항목별 전체 Gate 요약",
        "packet_preview": "CMC RA Decision Packet 미리보기",
        "markdown_preview": "Markdown 미리보기",
    },
    "en": {
        "page_title": "ToxiGuard Platform Ver.3",
        "subtitle": "CMC RA Evidence Workbench",
        "positioning": "A Streamlit workbench that connects CTD 3.2.P evidence, specification rationale, DMF linkage, calculation/validation review, and CMC RA response writing.",
        "language": "Language",
        "product_profile": "Product Profile",
        "client_intake": "Client CTD Intake",
        "document_workspace": "00 Document Input",
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
        "document_workspace_help": "Capture editable source-document inputs for DMF, CTD 3.2.S, CTD 3.2.P, and other CTD modules according to the product profile.",
        "evidence_map_help": "Manage P.1-P.8 evidence status by source, owner, risk, and next action.",
        "spec_help": "Missing criteria or weak rationale should become reviewer questions.",
        "dmf_help": "Check whether API DMF information supports DP CQA, specification, stability, and impurity strategy.",
        "calc_help": "Review sample preparation and result gates by assay, related substances, dissolution, elemental impurities, and nitrosamines.",
        "response_help": "Convert gaps into deficiency questions, needed evidence, and CTD update locations.",
        "download": "Download Decision Packet",
        "sample_prep": "Test-Specific Sample Preparation Review",
        "validation_gate": "Test-Specific Validation Result Gate",
        "risk_notes": "Automatic Risk Notes",
        "available_apps": "Available Apps",
        "next_builds": "Next Builds",
        "meeting_summary": "Client Meeting Summary",
        "client_questions": "Client Question List",
        "ctd_update_direction": "CTD Update Direction",
        "enter_workbench": "Enter Workbench",
        "landing_enter_note": "Click the image or button to enter the app",
        "selected": "Selected",
        "open_review": "Open review",
        "live": "Live",
        "risk_watch": "Risk watch",
        "decision_context": "Decision context",
        "intake_readiness": "Intake readiness",
        "client_document_usability": "Client document usability",
        "source_readiness": "3.2.S/P source readiness",
        "ctd_document_readiness": "CTD document readiness",
        "dmf_document_readiness": "DMF document readiness",
        "source_text_entries": "Source text entries",
        "profile_driven_prompts": "Product-profile-driven questions",
        "dmf_source_input": "DMF Source Input",
        "ctd_3_2_s_input": "CTD 3.2.S Drug Substance Input",
        "ctd_3_2_p_input": "CTD 3.2.P Drug Product Input",
        "ctd_other_parts_input": "Other CTD Module Input",
        "ctd_module_strategy": "CTD Module Strategy",
        "document_input_strategy": "Module 3 is handled as detailed CMC evidence; Modules 1/2/4/5 are captured as regulatory, clinical, nonclinical, and change-impact context linked back to CMC decisions.",
        "company_document_flow": "Company Document Application Flow",
        "document_logic": "Document Application Logic",
        "document_logic_help": "An editable operating rule that turns real company documents into CMC judgement questions, CTD update locations, and follow-up actions.",
        "key_decision_points": "Key Decision Points",
        "document_review_boundary": "The app does not finalize document conclusions. It organizes risk questions from source text and confirmed values so the CMC RA expert can edit and decide.",
        "apply_document_inputs": "Apply Document Inputs to Workbench",
        "apply_document_inputs_help": "Push current DMF/CTD inputs into the 3.2.S/P Evidence Map, DMF-to-DP Bridge, and P.5.6 risk seed.",
        "apply_document_inputs_done": "Document inputs were applied to the workbench.",
        "raw_document_paste": "Long source-document excerpt / note",
        "questions_to_ask": "Questions to ask in meeting",
        "product": "Product",
        "active_substance": "Active substance / API",
        "api_supplier": "API supplier / DMF holder",
        "formulation_platform": "Formulation technology / platform",
        "clinical_material": "Clinical trial material / batch",
        "target_regions": "Target regions",
        "dosage_form": "Dosage form",
        "strength": "Strength",
        "route": "Route",
        "reference": "Reference / comparator",
        "lifecycle_stage": "Lifecycle stage",
        "github_target": "GitHub target",
        "document_received": "Document received",
        "input": "Input",
        "gap_risk_summary": "Gap / risk summary",
        "ctd_direction": "CTD direction",
        "meeting_ready_view": "Meeting-ready view",
        "evidence_request_list": "Evidence request list",
        "update_target_section": "Update target section",
        "status": "Status",
        "risk": "Risk",
        "quality": "Quality",
        "received": "Received",
        "validation_select": "Test-specific validation review",
        "validation_basis": "Review basis",
        "regulatory_basis": "Regulatory basis",
        "ctd_location": "CTD location",
        "m14_note": "ICH M14 note",
        "result_inputs": "Required result inputs",
        "validation_review_warning": "validation result item(s) need review before the Decision Packet is treated as ready.",
        "validation_review_success": "Validation result gate is passing for the selected test item.",
        "overall_validation_summary": "Overall validation item summary",
        "packet_preview": "CMC RA Decision Packet Preview",
        "markdown_preview": "Markdown preview",
    },
}


COLUMN_KO: dict[str, str] = {
    "Intake area": "접수 항목",
    "Expected client document": "필요 고객 문서",
    "Received": "수신 상태",
    "Quality": "문서 품질",
    "Risk": "리스크",
    "Consultant check": "컨설턴트 확인사항",
    "Client question": "고객 질문",
    "CTD update direction": "CTD 업데이트 방향",
    "CTD section": "CTD 항목",
    "CTD module": "CTD 모듈",
    "CTD part": "CTD 파트",
    "Document group": "문서군",
    "DMF section": "DMF 항목",
    "Expected information": "필요 정보",
    "Document source": "문서 출처",
    "Document text / excerpt": "문서 원문 / 발췌",
    "Confirmed value": "확인값",
    "Evidence use": "근거 활용",
    "Product linkage": "제품 연결성",
    "DP linkage": "완제 연결성",
    "Profile signal": "제품 프로필 신호",
    "Evidence impact": "근거 영향",
    "Risk question": "리스크 질문",
    "Review stage": "검토 단계",
    "Input document": "입력 문서",
    "What to capture": "확인할 정보",
    "Where to apply": "적용 위치",
    "Decision point": "판단 포인트",
    "Why it matters": "중요한 이유",
    "CMC risk if unclear": "불명확할 때의 CMC 리스크",
    "Output artifact": "산출물",
    "Priority": "우선순위",
    "Source area": "근거 영역",
    "Source item": "근거 항목",
    "Key point": "핵심 포인트",
    "Evidence required": "필요 근거",
    "Affected CTD": "영향 CTD",
    "Suggested action": "제안 조치",
    "User decision": "사용자 판단",
    "Core question": "핵심 질문",
    "Status": "상태",
    "Source document": "근거 문서",
    "Owner": "담당",
    "Next action": "다음 조치",
    "Test item": "시험항목",
    "Acceptance criterion": "기준",
    "Method": "시험방법",
    "Validation status": "밸리데이션 상태",
    "Rationale basis": "설정 근거",
    "Linked CQA": "연결 CQA",
    "Reviewer question": "심사자 질문",
    "DMF element": "DMF 요소",
    "API / supplier evidence": "API / 공급자 근거",
    "DP impact": "완제 영향",
    "Applicant verification": "신청자 확인",
    "Action": "조치",
    "Field": "항목",
    "Value": "값",
    "Question": "질문",
    "Triggered by": "발생 원인",
    "Evidence needed": "필요 근거",
    "CTD update": "CTD 수정",
    "App": "앱",
    "Role": "역할",
    "Run": "실행",
    "Purpose": "목적",
    "Item": "항목",
    "Result": "결과",
    "Unit": "단위",
    "Rule": "판정 규칙",
    "Lower": "하한",
    "Upper": "상한",
    "Note": "메모",
    "Gate": "Gate",
    "Review items": "검토 항목",
    "Info items": "정보 항목",
    "Result rows": "결과 행",
    "Regulatory basis": "규제 근거",
    "Q14 check": "Q14 확인 항목",
    "Problem signal": "문제 신호",
    "Evidence to request": "요청할 근거",
    "Q14 anchor": "Q14 근거축",
    "Threshold": "기준",
    "Limit (%)": "한도 (%)",
    "Basis": "근거",
    "Method concentration (ug/mL)": "방법 농도 (ug/mL)",
    "Element": "원소",
    "ICH Q3D class": "ICH Q3D 분류",
    "Default scope": "기본 범위",
    "Route PDE entered (ug/day)": "입력 PDE (ug/day)",
    "Permitted concentration (ug/g)": "허용농도 (ug/g)",
    "Control threshold concentration (ug/g)": "Control threshold 농도 (ug/g)",
    "LOQ / target (%)": "LOQ / target (%)",
    "Calculated LOQ vs control threshold (ug/g)": "계산 LOQ vs control threshold (ug/g)",
    "Spike recovery (%)": "Spike 회수율 (%)",
    "Precision RSD (%)": "정밀성 RSD (%)",
    "Source / risk question": "출처 / 리스크 질문",
    "Route": "투여경로",
    "Control target / J-value note": "Control target / J값 메모",
}


VALUE_KO: dict[str, str] = {
    "Ready": "준비됨",
    "Partial": "일부 필요",
    "Gap": "공백",
    "N/A": "해당 없음",
    "Low": "낮음",
    "Medium": "중간",
    "High": "높음",
    "Received": "수신",
    "Missing": "누락",
    "Usable": "사용 가능",
    "Needs clarification": "확인 필요",
    "Not usable": "사용 불가",
    "Validated": "완료",
    "Not validated": "미완료",
    "Verified": "확인 완료",
    "Development": "개발",
    "Validation": "밸리데이션",
    "Submission prep": "허가자료 준비",
    "Response": "보완 답변",
    "Lifecycle change": "변경 관리",
    "Pass": "통과",
    "Review": "검토",
    "Info": "정보",
    "Critical": "최우선",
    "Hold": "보류",
    "Go": "진행",
    "Watch": "주의",
    "Open": "진행 중",
    "Accept": "수용",
    "Revise": "수정",
    "Escalate": "전문가 검토",
}


KO_TO_VALUE: dict[str, str] = {value: key for key, value in VALUE_KO.items()}
KO_TO_COLUMN: dict[str, str] = {value: key for key, value in COLUMN_KO.items()}


CONTENT_KO: dict[str, str] = {
    "Product profile / scope setting": "제품 프로필 / 검토 범위 설정",
    "Raw material / DMF intake": "원료 / DMF 접수",
    "Formulation development": "제형 개발",
    "Manufacturing process": "제조공정",
    "Specification and analytical control": "규격 및 분석 관리",
    "Stability and shelf-life": "안정성 및 사용기간",
    "Clinical material bridge": "임상시험용 의약품 연결성",
    "Regional submission / response": "지역별 허가 / 보완 답변",
    "Which CTD modules and CMC documents are actually needed for this product?": "이 제품에 실제로 필요한 CTD 모듈과 CMC 문서는 무엇인가?",
    "Does the API package support the drug product formula, clinical material, and final quality strategy?": "API 패키지가 완제 조성, 임상시험용 의약품, 최종 품질전략을 지지하는가?",
    "Can the selected formulation be defended as clinically relevant and commercially reproducible?": "선택한 제형이 임상적으로 타당하고 상업적으로 재현 가능하다고 방어할 수 있는가?",
    "Do process controls explain and protect the critical quality attributes?": "공정 관리가 핵심품질특성(CQA)을 설명하고 보호하는가?",
    "Is each quality criterion supported by data, validated method capability, safety or performance relevance, and batch/stability history?": "각 품질기준이 배치자료, 안정성, 밸리데이션된 분석능, 안전성 또는 성능 관련성으로 뒷받침되는가?",
    "Does the stability package support the proposed shelf-life and the selected release/stability specification?": "안정성 패키지가 제안 사용기간과 출하/안정성 규격을 지지하는가?",
    "Can the clinical trial material represent the proposed commercial drug product?": "임상시험용 의약품이 제안 상업제품을 대표한다고 설명할 수 있는가?",
    "Where should the answer live in CTD, and which source evidence makes it defensible?": "답변은 CTD 어디에 반영되어야 하며, 어떤 원문 근거가 이를 방어 가능하게 하는가?",
    "Documents may be reviewed without the product context needed to judge formulation, process, specification, and regional expectations.": "제품 맥락 없이 문서를 검토하면 제형, 공정, 규격, 지역별 요구사항 판단이 빗나갈 수 있습니다.",
    "A wrong raw-material assumption can affect formula calculation, impurity limits, release profile, stability, and later comparability arguments.": "원료에 대한 잘못된 가정은 조성 계산, 불순물 기준, 방출 profile, 안정성, 이후 comparability 논리에 영향을 줄 수 있습니다.",
    "A late formulation change can become a comparability, stability, nonclinical, clinical, or reviewer-question issue.": "늦은 제형 변경은 comparability, 안정성, 비임상, 임상 또는 심사자 질문 이슈로 커질 수 있습니다.",
    "Process or scale changes may alter particle attributes, release, residual solvent, sterility assurance, or stability trend.": "공정 또는 scale 변경은 입자 특성, 방출, 잔류용매, 무균보증, 안정성 trend를 바꿀 수 있습니다.",
    "Unsupported limits or calculation errors can make the specification indefensible even when the table itself looks complete.": "표가 완성되어 보여도, 근거 없는 기준이나 계산 오류가 있으면 규격은 방어하기 어렵습니다.",
    "Late stability drift can force shelf-life reduction, specification revision, additional batches, or agency questions.": "후기 안정성 drift는 사용기간 축소, 규격 수정, 추가 배치, 규제기관 질문으로 이어질 수 있습니다.",
    "A major CMC difference can trigger bridging, comparability justification, additional stability, nonclinical, clinical, or regulatory review needs.": "중대한 CMC 차이는 bridging, comparability 설명, 추가 안정성, 비임상, 임상 또는 규제 검토 필요성을 만들 수 있습니다.",
    "A response can sound plausible but fail because it is not anchored to the correct CTD section or source document.": "답변 문구가 그럴듯해도 올바른 CTD 위치와 원문 근거에 묶이지 않으면 방어력이 떨어집니다.",
    "The product profile determines which DMF and CTD evidence is applicable.": "제품 프로필은 어떤 DMF 및 CTD 근거가 적용되는지를 결정합니다.",
    "Use the profile to decide document request scope before judging sufficiency.": "문서 충분성을 판단하기 전에 제품 프로필로 요청 문서 범위를 먼저 정하세요.",
    "Confirm product profile before judging document sufficiency.": "문서가 충분한지 판단하기 전에 제품 프로필을 먼저 확정하세요.",
    "Request source text and confirmed values for API identity, grade, specification, impurity, and retest controls.": "API 동일성, grade, 규격, 불순물, retest 관리에 대한 원문 발췌와 확인값을 요청하세요.",
    "Link formulation variables to release, stability, manufacturability, and specification rationale.": "제형 변수를 방출, 안정성, 제조가능성, 기준설정 근거와 연결하세요.",
    "Trace each critical step to CQA, IPC, batch analysis, and stability evidence.": "각 중요 공정단계를 CQA, IPC, 배치분석, 안정성 근거와 추적 연결하세요.",
    "Convert every missing rationale into a reviewer question and evidence request.": "누락된 모든 설정 근거를 심사자 질문과 근거 요청으로 전환하세요.",
    "Connect trend evidence to acceptance criteria, degradation risk, and shelf-life justification.": "Trend 근거를 허용기준, 분해 리스크, 사용기간 설정 근거와 연결하세요.",
    "List each post-clinical CMC difference and define the needed bridge evidence.": "임상 이후 CMC 차이를 항목별로 정리하고 필요한 bridge 근거를 정의하세요.",
    "Write responses only after the source evidence, CTD location, and owner are traceable.": "원문 근거, CTD 위치, 담당자가 추적 가능할 때 답변을 작성하세요.",
    "Product-profile-driven review prompts": "제품 프로필 기반 검토 질문",
    "DMF-to-DP bridge and API evidence request list": "DMF-to-DP bridge 및 API 근거 요청 리스트",
    "P.2 evidence map and formulation-risk memo": "P.2 근거 맵 및 제형 리스크 메모",
    "Manufacturing control and clinical-batch representativeness note": "제조 관리 및 임상 배치 대표성 메모",
    "P.5.6 rationale and calculation/validation review memo": "P.5.6 기준설정 근거 및 계산/밸리데이션 검토 메모",
    "Stability evidence and commitment map": "안정성 근거 및 commitment map",
    "Clinical-material representativeness memo": "임상시험용 의약품 대표성 메모",
    "CMC RA response memo and CTD update action table": "CMC RA 답변 메모 및 CTD 업데이트 action table",
    "API identity, grade, salt/form, potency/water correction, impurity carryover": "API 동일성, grade, 염/형태, 역가/수분 보정, 불순물 carryover",
    "DMF access, supplier qualification, change notification, manufacturing-site traceability": "DMF 접근권, 공급자 qualification, 변경 통지, 제조소 추적성",
    "QTPP/CQA, formulation variables, process design, release profile, manufacturability": "QTPP/CQA, 제형 변수, 공정 설계, 방출 profile, 제조가능성",
    "Clinical batch genealogy, representativeness, comparability, bridging risk": "임상 배치 계보, 대표성, comparability, bridging 리스크",
    "Regional Module 1 expectations, QOS narrative, CTD placement, agency response style": "지역별 Module 1 요구사항, QOS narrative, CTD 반영 위치, 규제기관 답변 방식",
    "Is the API used for clinical material the same material strategy intended for the final DP?": "임상시험용 의약품에 사용된 API가 최종 완제 전략과 동일한 material strategy인가?",
    "Can the applicant defend the current DMF version and supplier commitment?": "신청자가 현재 DMF 버전과 공급자 commitment를 방어할 수 있는가?",
    "Does the formulation platform remain bridgeable from clinical to commercial product?": "이 제형 플랫폼은 임상제품에서 상업제품으로 bridge 가능하게 유지되는가?",
    "Can the clinical trial material be justified as representative of the proposed commercial product?": "임상시험용 의약품이 제안 상업제품을 대표한다고 설명할 수 있는가?",
    "Which regional requirements change the evidence package or CTD update location?": "어떤 지역별 요구사항이 근거 패키지나 CTD 반영 위치를 바꾸는가?",
    "Is API identity, nomenclature, structure, salt form, and physicochemical profile defined?": "API 동일성, 명칭, 구조, 염 형태, 물리화학적 특성이 정의되어 있는가?",
    "Are API manufacturer, route, critical steps, controls, and change notification traceable?": "API 제조원, 제조경로, 중요 단계, 관리전략, 변경 통지가 추적 가능한가?",
    "Are API impurities, degradation pathways, polymorph/PSD/water attributes characterized for DP impact?": "API 불순물, 분해경로, 결정형/PSD/수분 특성이 완제 영향 관점에서 characterization 되어 있는가?",
    "Do API specifications, methods, validation, batch results, and justification support DP control strategy?": "API 규격, 시험방법, 밸리데이션, 배치 결과, 설정 근거가 완제 관리전략을 지지하는가?",
    "Does API retest period, storage condition, and packaging support DP manufacturing and shelf-life strategy?": "API retest period, 보관조건, 포장이 완제 제조와 사용기간 전략을 지지하는가?",
    "Is product identity, composition, strength, route, and packaging clearly defined?": "제품 동일성, 조성, 함량, 투여경로, 포장이 명확히 정의되어 있는가?",
    "Does development rationale support QTPP, CQA, formulation, and process choices?": "개발 근거가 QTPP, CQA, 제형 및 공정 선택을 지지하는가?",
    "Can the commercial process and IPC strategy consistently produce target quality?": "상업 공정과 IPC 전략이 목표 품질을 일관되게 만들 수 있는가?",
    "Do specifications, methods, validation, and batch data support release and shelf-life quality?": "규격, 시험방법, 밸리데이션, 배치자료가 출하 및 사용기간 품질을 지지하는가?",
    "Does container closure evidence support compatibility, protection, and use?": "용기마개 근거가 적합성, 보호성, 사용성을 지지하는가?",
    "Do stability data support proposed storage condition and shelf-life?": "안정성 자료가 제안 보관조건과 사용기간을 지지하는가?",
    "Complete P.5.6 rationale and validation gate review.": "P.5.6 설정 근거와 밸리데이션 gate 검토를 완료하세요.",
    "Add trend table, shelf-life justification, and commitment.": "Trend table, 사용기간 설정 근거, commitment를 추가하세요.",
    "Is assay basis aligned with API potency and water correction?": "함량 기준이 API 역가 및 수분 보정과 일치하는가?",
    "Are degradation products qualified and controlled through shelf-life?": "분해산물이 사용기간 동안 qualification 및 관리되는가?",
    "Does the method discriminate formulation or process changes?": "시험방법이 제형 또는 공정 변경을 구분할 수 있는가?",
    "Is particle size linked to release profile and stability?": "입자도가 방출 profile 및 안정성과 연결되어 있는가?",
    "Is solvent removal controlled by process parameters?": "잔류용매 제거가 공정변수로 관리되는가?",
    "Is sterility assurance strategy supported by process validation?": "무균보증 전략이 공정 밸리데이션으로 뒷받침되는가?",
    "Regulatory reference for API quality sections": "API 품질 항목에 대한 규제상 참조 근거",
    "Batch formula, assay calculation, label claim": "배치 조성, 함량 계산, 표시량",
    "Potency correction, stability, process moisture risk": "역가 보정, 안정성, 공정 중 수분 리스크",
    "Related substances specification and stability trend": "유연물질 규격 및 안정성 trend",
    "Manufacturing hold time, stability commitment": "제조 hold time, 안정성 commitment",
    "Confirm current DMF version and holder commitment.": "현재 DMF 버전과 holder commitment를 확인하세요.",
    "Align potency correction with assay and sample prep calculation.": "역가 보정을 함량시험 및 시료 제조 계산과 정렬하세요.",
    "Check water impact on actual theoretical value.": "수분이 실제 이론값에 미치는 영향을 확인하세요.",
    "Bridge API PSD to DP CQA and method control.": "API PSD를 완제 CQA 및 시험방법 관리와 bridge 하세요.",
    "Separate API impurity from DP degradant and qualify risk.": "API 불순물과 완제 분해산물을 분리하고 리스크를 qualification 하세요.",
    "Check whether API storage supports DP manufacturing timeline.": "API 보관 조건이 완제 제조 일정을 지지하는지 확인하세요.",
    "Supports applicant right of reference and CTD 3.2.S cross-reference": "신청자의 참조권 및 CTD 3.2.S cross-reference를 지지",
    "Defines the drug substance used in formula, assay basis, and clinical material bridge": "조성, 함량 기준, 임상시험용 의약품 bridge에 사용되는 원료의약품을 정의",
    "Affects starting material control, impurity risk, and post-change comparability planning": "출발물질 관리, 불순물 리스크, 변경 후 comparability 계획에 영향",
    "Feeds DP related substances, stability trend, ICH M7/Q3B rationale": "완제 유연물질, 안정성 trend, ICH M7/Q3B 근거로 연결",
    "Supports DP formula, assay correction, processability, release, and stability controls": "완제 조성, 함량 보정, 공정성, 방출, 안정성 관리를 지지",
    "Supports manufacturing hold time, clinical material usage, and DP shelf-life strategy": "제조 hold time, 임상시험용 의약품 사용, 완제 사용기간 전략을 지지",
    "API identity anchor for formula, assay, and DMF bridge": "조성, 함량, DMF bridge의 API 동일성 anchor",
    "Supplier/change-control risk and API process impurity context": "공급자/변경관리 리스크 및 API 공정 불순물 맥락",
    "Links API attributes to DP CQA, P.5.5, P.5.6, and P.8": "API 특성을 완제 CQA, P.5.5, P.5.6, P.8과 연결",
    "Supports API-to-DP bridge, assay basis, impurity limits, and processability": "API-to-DP bridge, 함량 기준, 불순물 기준, 공정성을 지지",
    "Connects early CMC decisions to clinical material and final product design": "초기 CMC 의사결정을 임상시험용 의약품 및 최종 제품 설계와 연결",
    "Supports manufacturability, clinical batch representativeness, and change-risk control": "제조가능성, 임상 배치 대표성, 변경 리스크 관리를 지지",
    "Main reviewer-facing control strategy and acceptance-criterion rationale": "심사자에게 직접 보이는 핵심 관리전략 및 허용기준 설정 근거",
    "Supports release/stability criteria, impurity limits, storage, and clinical/commercial bridge": "출하/안정성 기준, 불순물 기준, 보관, 임상/상업 bridge를 지지",
    "Flags whether CMC changes may require bridging, additional justification, or expert review": "CMC 변경이 bridging, 추가 설명, 전문가 검토를 요구할 수 있는지 표시",
    "Confirm API form and grade against clinical/commercial material.": "임상/상업 material 기준으로 API form과 grade를 확인하세요.",
    "Request current DMF version, LoA, site, and change notification basis.": "현재 DMF 버전, LoA, 제조소, 변경 통지 근거를 요청하세요.",
    "Map API impurities, water, PSD, and polymorph to DP control strategy.": "API 불순물, 수분, PSD, 결정형을 완제 관리전략에 mapping 하세요.",
    "Compare API criteria against DP CQA and validation calculations.": "API 기준을 완제 CQA 및 밸리데이션 계산과 비교하세요.",
    "Complete specification rationale, validation gate, calculation check, and batch/stability linkage.": "기준설정 근거, 밸리데이션 gate, 계산 검토, 배치/안정성 연결성을 완료하세요.",
    "Add trend table, release-profile drift review, degradation risk, and commitment plan.": "Trend table, 방출 profile drift 검토, 분해 리스크, commitment plan을 추가하세요.",
}


KO_TO_CONTENT: dict[str, str] = {value: key for key, value in CONTENT_KO.items()}
BODY_TRANSLATION_COLUMNS = {
    "Intake area",
    "Expected client document",
    "Consultant check",
    "Client question",
    "CTD update direction",
    "Core question",
    "Source document",
    "Next action",
    "Test item",
    "Acceptance criterion",
    "Method",
    "Rationale basis",
    "Linked CQA",
    "Reviewer question",
    "DMF element",
    "API / supplier evidence",
    "DP impact",
    "Action",
    "Expected information",
    "Confirmed value",
    "Evidence use",
    "DP linkage",
    "Review stage",
    "Input document",
    "What to capture",
    "Where to apply",
    "Decision point",
    "Why it matters",
    "CMC risk if unclear",
    "Output artifact",
    "Source area",
    "Key point",
    "Evidence required",
    "Affected CTD",
    "Suggested action",
    "Evidence impact",
    "Risk question",
    "Question",
    "Triggered by",
    "Evidence needed",
    "CTD update",
    "Role",
    "Purpose",
}


PROFILE_COPY_KO: dict[str, dict[str, str]] = {
    "assay": {
        "purpose": "API 역가/수분 보정, 표시량, 100% 기준농도의 연결성을 확인합니다.",
        "sample_focus": "100% 표시량 기준농도를 중심으로 제조합니다. 실제 칭량량, 순도/수분 보정, stock 부피, 취한량, 최종부피, 추가 희석배수를 모두 반영합니다.",
        "m14": "ICH M14는 분석법 밸리데이션의 적합 기준이 아닙니다. 노출량 또는 실제 임상 안전성 해석이 논의될 때 safety evidence 추적성 관점의 참고로만 사용합니다.",
    },
    "related_substances": {
        "purpose": "보고, 확인, 안전성 확인 기준에 따라 기지/미지 유연물질과 분해산물을 관리합니다.",
        "sample_focus": "기준농도는 함량 100%가 아니라 유연물질 보고기준 또는 규격 수준과 맞아야 합니다. 낮은 농도 spike와 LOQ 근거가 핵심입니다.",
        "m14": "ICH M14는 유연물질 노출이 시판 후 또는 실제 임상 안전성 근거와 연결될 때 safety question framing을 보조할 수 있습니다. 그러나 유연물질 qualification이나 분석법 밸리데이션 기준을 대체하지는 않습니다.",
    },
    "dissolution": {
        "purpose": "시간별 용출률, profile 비교, 완전용출 기준농도와 시료 희석 흐름을 확인합니다.",
        "sample_focus": "완전용출 후 명목농도 또는 각 시간점 정량농도를 기준으로 잡습니다. 필터, 용출액, sink condition, 희석 흐름을 추적할 수 있어야 합니다.",
        "m14": "ICH M14는 용출 성능을 임상 또는 real-world safety/effectiveness 질문과 연결하는 데 도움을 줄 수 있습니다. 다만 분석법 밸리데이션은 여전히 분석 성능과 제품 성능 근거로 판단합니다.",
    },
    "elemental_impurities": {
        "purpose": "ICP 분석능, PDE/control threshold, 제품별 금속불순물 risk assessment를 연결합니다.",
        "sample_focus": "기준농도는 PDE, 최대일일복용량, J값/control threshold와 연결되어야 합니다. 산분해와 matrix spike recovery가 핵심입니다.",
        "m14": "ICH M14는 금속 노출을 real-world safety data와 함께 해석할 때 safety follow-up 관점을 제공할 수 있습니다. CMC control 판단은 Q3D와 검증된 분석능에 기반해야 합니다.",
    },
    "nitrosamines": {
        "purpose": "허용섭취량과 제품별 니트로사민 리스크에 맞춰 고감도 trace-level 분석능을 확인합니다.",
        "sample_focus": "기준농도는 허용섭취량, 최대일일복용량, 시료농도에서 도출해야 합니다. Matrix effect, carryover, isotope/internal standard 성능이 중요합니다.",
        "m14": "ICH M14는 니트로사민 결과를 실제 노출 또는 안전성 질문과 연결할 때 보조적인 safety evidence layer로만 활용합니다. CMC 분석법 밸리데이션 규칙 자체는 아닙니다.",
    },
}


MODULES = [
    {
        "no": "0",
        "icon": "clipboard_check",
        "tone": "teal",
        "title": "Client CTD Intake",
        "title_ko": "고객 CTD 문서 접수",
        "status": "Live in Ver.3",
        "output": "Document received, intake quality, client questions, CTD update direction",
        "output_ko": "접수 문서, 문서 품질, 고객 질문, CTD 업데이트 방향",
        "risk": "Client document is received but not traceable to DMF, DP process, specification, or CTD section",
        "risk_ko": "문서는 받았지만 DMF, 완제 공정, 규격, CTD 항목과 추적 연결되지 않은 상태",
    },
    {
        "no": "1",
        "icon": "network",
        "tone": "teal",
        "title": "3.2.P Evidence Map",
        "title_ko": "3.2.P 근거 맵",
        "status": "Live in Ver.3",
        "output": "P.1-P.8 evidence map, gap list, reviewer question seed",
        "output_ko": "P.1-P.8 근거 맵, gap 리스트, 심사자 질문 seed",
        "risk": "Missing source traceability or undefined CTD owner",
        "risk_ko": "근거 출처 추적성 누락 또는 CTD 담당자 미정",
    },
    {
        "no": "2",
        "icon": "target",
        "tone": "amber",
        "title": "P.5.6 Specification Rationale",
        "title_ko": "P.5.6 기준 설정 근거",
        "status": "Live in Ver.3",
        "output": "Specification rationale table and acceptance criteria memo",
        "output_ko": "품질기준 설정 근거표와 acceptance criteria 메모",
        "risk": "Acceptance criterion without batch, stability, validation, or literature basis",
        "risk_ko": "배치, 안정성, 밸리데이션, 문헌 근거 없이 설정된 기준",
    },
    {
        "no": "3",
        "icon": "bridge",
        "tone": "blue",
        "title": "DMF-to-DP Bridge",
        "title_ko": "DMF-완제 연결성",
        "status": "Live in Ver.3",
        "output": "API-to-drug-product bridge table and change impact note",
        "output_ko": "원료-완제 연결표와 변경 영향 메모",
        "risk": "API potency, water, PSD, polymorph, impurity, or retest mismatch",
        "risk_ko": "API 역가, 수분, PSD, 결정형, 불순물, retest 기준 불일치",
    },
    {
        "no": "4",
        "icon": "calculator",
        "tone": "orange",
        "title": "Calculation / Validation Review",
        "title_ko": "계산 / 밸리데이션 검토",
        "status": "Live in Ver.3 + SOP Gate link",
        "output": "Sample prep concentration, dilution factor, LOD/LOQ %, intercept risk",
        "output_ko": "시료 제조 농도, 희석배수, LOD/LOQ %, intercept 리스크",
        "risk": "Reference concentration or dilution factor not reflected in validation level",
        "risk_ko": "기준농도 또는 희석배수가 밸리데이션 level에 반영되지 않음",
    },
    {
        "no": "5",
        "icon": "file_pen",
        "tone": "green",
        "title": "CMC RA Response Memo",
        "title_ko": "CMC RA 답변 메모",
        "status": "Live in Ver.3 draft",
        "output": "Response memo, required evidence, CTD update action table",
        "output_ko": "답변 메모, 필요 근거, CTD 업데이트 action table",
        "risk": "Answer draft not connected to source evidence or owner",
        "risk_ko": "답변 초안이 근거 문서 또는 담당자와 연결되지 않음",
    },
]


NAV_ITEMS = [
    {
        "key": "intake",
        "label_key": "client_intake",
        "description": "Client document intake",
        "description_ko": "고객 문서 접수",
        "icon": "clipboard_check",
        "tone": "teal",
    },
    {
        "key": "documents",
        "label_key": "document_workspace",
        "description": "DMF and CTD source input",
        "description_ko": "DMF·CTD 원문 입력",
        "icon": "file_pen",
        "tone": "blue",
    },
    {
        "key": "dashboard",
        "label_key": "dashboard",
        "description": "Evidence overview",
        "description_ko": "근거 현황",
        "icon": "gauge",
        "tone": "blue",
    },
    {
        "key": "evidence",
        "label_key": "evidence_map",
        "description": "CTD source map",
        "description_ko": "CTD 근거 맵",
        "icon": "network",
        "tone": "teal",
    },
    {
        "key": "spec",
        "label_key": "spec_rationale",
        "description": "P.5.6 rationale",
        "description_ko": "기준 설정 근거",
        "icon": "target",
        "tone": "amber",
    },
    {
        "key": "dmf",
        "label_key": "dmf_bridge",
        "description": "API-to-DP bridge",
        "description_ko": "원료-완제 연결",
        "icon": "bridge",
        "tone": "blue",
    },
    {
        "key": "validation",
        "label_key": "validation",
        "description": "Concentration gate",
        "description_ko": "농도 검토 Gate",
        "icon": "calculator",
        "tone": "orange",
    },
    {
        "key": "response",
        "label_key": "response",
        "description": "RA response memo",
        "description_ko": "RA 답변 메모",
        "icon": "file_pen",
        "tone": "green",
    },
    {
        "key": "launcher",
        "label_key": "launcher",
        "description": "Connected apps",
        "description_ko": "연결 앱",
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
    "vial": '<path d="M9 2.8h6"/><path d="M10 2.8v5.5l-4.1 7.4A3.8 3.8 0 0 0 9.2 21h5.6a3.8 3.8 0 0 0 3.3-5.3L14 8.3V2.8"/><path d="M8 15h8"/>',
    "impurity": '<circle cx="7" cy="8" r="3"/><circle cx="16.5" cy="6.5" r="2.4"/><circle cx="15" cy="16" r="3.2"/><path d="m9.7 8.8 3.9 1.7"/><path d="m15.7 8.8-.4 3.9"/><path d="M7.8 10.8l4.6 3.4"/>',
    "dissolution": '<path d="M5 7h14"/><path d="M7 7v7.5A4.8 4.8 0 0 0 11.8 19h.4A4.8 4.8 0 0 0 17 14.5V7"/><path d="M8 13c1.2-1 2.5-1 3.8 0s2.7 1 4.2 0"/><path d="M10 3h4"/>',
    "atom": '<circle cx="12" cy="12" r="1.7"/><ellipse cx="12" cy="12" rx="8.5" ry="3.4"/><ellipse cx="12" cy="12" rx="8.5" ry="3.4" transform="rotate(60 12 12)"/><ellipse cx="12" cy="12" rx="8.5" ry="3.4" transform="rotate(120 12 12)"/>',
    "molecule": '<circle cx="5.8" cy="12" r="2.8"/><circle cx="15.8" cy="6.5" r="2.5"/><circle cx="17.6" cy="17.2" r="3"/><path d="m8.2 10.6 5.5-3"/><path d="m8.4 13.3 6.4 2.7"/><path d="M16.2 9.1l1 5.1"/>',
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


VALIDATION_TEST_ITEMS: list[dict[str, Any]] = [
    {
        "key": "assay",
        "label_ko": "함량",
        "label_en": "Assay",
        "icon": "vial",
        "tone": "blue",
        "purpose": "API potency/water correction, label claim, and 100% reference concentration alignment.",
        "sample_focus": "Prepare around the 100% label-claim concentration. Apply actual weighing, purity/water correction, stock volume, aliquot, final volume, and any additional dilution.",
        "ctd": "3.2.P.5.2 / 3.2.P.5.3 / 3.2.P.5.6",
        "basis": "ICH Q2(R2), ICH Q14, ICH Q6A",
        "m14": "ICH M14 is not the analytical validation acceptance basis. Use it only as a safety-evidence traceability prompt when exposure or real-world safety interpretation is discussed.",
        "prep_defaults": {
            "reference_conc": 2.5,
            "unit": "ug/mL",
            "level_pct": 100.0,
            "weighed_mg": 25.0,
            "purity_pct": 99.8,
            "stock_volume_ml": 100.0,
            "aliquot_ml": 1.0,
            "final_volume_ml": 50.0,
            "dilution_factor": 2.0,
        },
        "linearity_defaults": {
            "lod": 0.05,
            "loq": 0.15,
            "r2": 0.9992,
            "slope": 12450.0,
            "intercept": 240.0,
            "response_100": 31125.0,
            "response_loq": 1867.5,
            "lowest_level_pct": 80.0,
        },
        "rows": [
            {
                "Item": "Specificity interference",
                "Result": 0.12,
                "Unit": "% of assay response",
                "Rule": "lte",
                "Lower": None,
                "Upper": 0.2,
                "Note": "Blank/placebo/API impurity interference at assay retention time",
            },
            {
                "Item": "Linearity R2",
                "Result": 0.9992,
                "Unit": "",
                "Rule": "gte",
                "Lower": 0.999,
                "Upper": None,
                "Note": "Check intercept even when R2 passes",
            },
            {
                "Item": "Accuracy mean recovery",
                "Result": 99.1,
                "Unit": "%",
                "Rule": "between",
                "Lower": 98.0,
                "Upper": 102.0,
                "Note": "Usually evaluated around 80/100/120% assay levels",
            },
            {
                "Item": "Repeatability RSD",
                "Result": 1.1,
                "Unit": "%",
                "Rule": "lte",
                "Lower": None,
                "Upper": 2.0,
                "Note": "Six independent sample preparations",
            },
            {
                "Item": "Intermediate precision RSD",
                "Result": 1.8,
                "Unit": "%",
                "Rule": "lte",
                "Lower": None,
                "Upper": 2.0,
                "Note": "Different day, analyst, instrument, or column lot",
            },
            {
                "Item": "Robustness assay shift",
                "Result": 1.2,
                "Unit": "%",
                "Rule": "lte",
                "Lower": None,
                "Upper": 2.0,
                "Note": "Flow, wavelength, column temperature, mobile phase pH/composition",
            },
        ],
    },
    {
        "key": "related_substances",
        "label_ko": "유연물질",
        "label_en": "Related substances",
        "icon": "impurity",
        "tone": "amber",
        "purpose": "Control specified, unspecified, and degradation impurities against reporting/identification/qualification thresholds.",
        "sample_focus": "Reference concentration should match the impurity reporting or specification level, not only the assay 100% level. Low-level spike preparation and LOQ support are critical.",
        "ctd": "3.2.P.5.2 / 3.2.P.5.3 / 3.2.P.5.5 / 3.2.P.5.6",
        "basis": "ICH Q2(R2), ICH Q14, ICH Q3A(R2), ICH Q3B(R2)",
        "m14": "ICH M14 can support safety question framing if impurity exposure is connected to post-market or real-world safety evidence, but it does not replace impurity qualification or analytical validation rules.",
        "prep_defaults": {
            "reference_conc": 0.5,
            "unit": "ug/mL",
            "level_pct": 100.0,
            "weighed_mg": 5.0,
            "purity_pct": 98.5,
            "stock_volume_ml": 100.0,
            "aliquot_ml": 1.0,
            "final_volume_ml": 100.0,
            "dilution_factor": 1.0,
        },
        "linearity_defaults": {
            "lod": 0.01,
            "loq": 0.03,
            "r2": 0.9985,
            "slope": 9800.0,
            "intercept": 68.0,
            "response_100": 4900.0,
            "response_loq": 294.0,
            "lowest_level_pct": 50.0,
        },
        "rows": [
            {
                "Item": "Critical pair resolution",
                "Result": 1.8,
                "Unit": "Rs",
                "Rule": "gte",
                "Lower": 1.5,
                "Upper": None,
                "Note": "API impurity, degradant, placebo, and nearest peak separation",
            },
            {
                "Item": "Linearity R2",
                "Result": 0.9985,
                "Unit": "",
                "Rule": "gte",
                "Lower": 0.995,
                "Upper": None,
                "Note": "LOQ to at least 120-150% of specification or reporting level",
            },
            {
                "Item": "LOQ precision RSD",
                "Result": 8.5,
                "Unit": "%",
                "Rule": "lte",
                "Lower": None,
                "Upper": 10.0,
                "Note": "Low-level repeat injections or preparations at LOQ",
            },
            {
                "Item": "Accuracy at threshold level",
                "Result": 92.0,
                "Unit": "%",
                "Rule": "between",
                "Lower": 80.0,
                "Upper": 120.0,
                "Note": "Recovery at reporting/identification/specification levels",
            },
            {
                "Item": "Repeatability RSD",
                "Result": 6.2,
                "Unit": "%",
                "Rule": "lte",
                "Lower": None,
                "Upper": 10.0,
                "Note": "Independent impurity sample preparations",
            },
            {
                "Item": "Forced degradation mass balance",
                "Result": 97.0,
                "Unit": "%",
                "Rule": "between",
                "Lower": 95.0,
                "Upper": 105.0,
                "Note": "Supports specificity and stability-indicating claim",
            },
        ],
    },
    {
        "key": "dissolution",
        "label_ko": "용출",
        "label_en": "Dissolution",
        "icon": "dissolution",
        "tone": "teal",
        "purpose": "Confirm the method can measure release performance and discriminate formulation or process changes.",
        "sample_focus": "Reference concentration should reflect the nominal concentration after complete dissolution or profile timepoint quantitation. Filter, medium, sink condition, and dilution scheme must be traceable.",
        "ctd": "3.2.P.2 / 3.2.P.5.2 / 3.2.P.5.3 / 3.2.P.5.6",
        "basis": "ICH Q2(R2), ICH Q14, ICH Q6A",
        "m14": "ICH M14 may help connect dissolution performance to clinical or real-world safety/effectiveness questions, but method validation is still judged by analytical and product-performance evidence.",
        "prep_defaults": {
            "reference_conc": 20.0,
            "unit": "ug/mL",
            "level_pct": 100.0,
            "weighed_mg": 20.0,
            "purity_pct": 99.0,
            "stock_volume_ml": 100.0,
            "aliquot_ml": 5.0,
            "final_volume_ml": 50.0,
            "dilution_factor": 9.9,
        },
        "linearity_defaults": {
            "lod": 0.2,
            "loq": 0.6,
            "r2": 0.9990,
            "slope": 8700.0,
            "intercept": 320.0,
            "response_100": 174000.0,
            "response_loq": 5220.0,
            "lowest_level_pct": 20.0,
        },
        "rows": [
            {
                "Item": "Filter compatibility recovery",
                "Result": 99.0,
                "Unit": "%",
                "Rule": "between",
                "Lower": 98.0,
                "Upper": 102.0,
                "Note": "Filtered vs centrifuged or unfiltered reference solution",
            },
            {
                "Item": "Linearity R2",
                "Result": 0.9990,
                "Unit": "",
                "Rule": "gte",
                "Lower": 0.995,
                "Upper": None,
                "Note": "Range should cover early and late timepoint concentrations",
            },
            {
                "Item": "Accuracy mean recovery",
                "Result": 101.5,
                "Unit": "%",
                "Rule": "between",
                "Lower": 95.0,
                "Upper": 105.0,
                "Note": "Spike/recovery in dissolution medium",
            },
            {
                "Item": "Repeatability profile RSD",
                "Result": 4.2,
                "Unit": "%",
                "Rule": "lte",
                "Lower": None,
                "Upper": 5.0,
                "Note": "Typically stricter at later timepoints; early low release may justify wider review",
            },
            {
                "Item": "Intermediate precision mean difference",
                "Result": 6.5,
                "Unit": "%",
                "Rule": "lte",
                "Lower": None,
                "Upper": 10.0,
                "Note": "Different analyst/day/apparatus",
            },
            {
                "Item": "Discriminatory power",
                "Result": 1.0,
                "Unit": "rank-order flag",
                "Rule": "gte",
                "Lower": 1.0,
                "Upper": None,
                "Note": "Method should detect meaningful formulation or process change",
            },
        ],
    },
    {
        "key": "elemental_impurities",
        "label_ko": "금속불순물",
        "label_en": "Elemental impurities",
        "icon": "atom",
        "tone": "green",
        "purpose": "Connect ICP method capability, PDE/control threshold, and product-specific risk assessment.",
        "sample_focus": "Reference concentration should be connected to the permitted daily exposure, maximum daily dose, and J/control threshold. Acid digestion and matrix spike recovery are central.",
        "ctd": "3.2.P.5.2 / 3.2.P.5.3 / 3.2.P.5.5 / 3.2.P.5.6",
        "basis": "ICH Q2(R2), ICH Q14, ICH Q3D(R2)",
        "m14": "ICH M14 can frame safety follow-up if elemental exposure is interpreted with real-world safety data. The CMC control decision remains anchored to Q3D and validated method capability.",
        "prep_defaults": {
            "reference_conc": 0.3,
            "unit": "ug/g or ppm",
            "level_pct": 100.0,
            "weighed_mg": 500.0,
            "purity_pct": 100.0,
            "stock_volume_ml": 50.0,
            "aliquot_ml": 1.0,
            "final_volume_ml": 100.0,
            "dilution_factor": 333.3333,
        },
        "linearity_defaults": {
            "lod": 0.01,
            "loq": 0.03,
            "r2": 0.9991,
            "slope": 6200.0,
            "intercept": 8.0,
            "response_100": 1860.0,
            "response_loq": 186.0,
            "lowest_level_pct": 30.0,
        },
        "rows": [
            {
                "Item": "LOQ / control threshold",
                "Result": 10.0,
                "Unit": "%",
                "Rule": "lte",
                "Lower": None,
                "Upper": 30.0,
                "Note": "LOQ should be meaningfully below the J/control threshold",
            },
            {
                "Item": "Calibration R2",
                "Result": 0.9991,
                "Unit": "",
                "Rule": "gte",
                "Lower": 0.995,
                "Upper": None,
                "Note": "Matrix-matched or appropriately corrected calibration",
            },
            {
                "Item": "Spike recovery",
                "Result": 92.0,
                "Unit": "%",
                "Rule": "between",
                "Lower": 70.0,
                "Upper": 150.0,
                "Note": "Matrix spike recovery across representative elements",
            },
            {
                "Item": "Repeatability RSD",
                "Result": 12.0,
                "Unit": "%",
                "Rule": "lte",
                "Lower": None,
                "Upper": 20.0,
                "Note": "Independent digestions or preparations",
            },
            {
                "Item": "Intermediate precision RSD",
                "Result": 18.0,
                "Unit": "%",
                "Rule": "lte",
                "Lower": None,
                "Upper": 25.0,
                "Note": "Different day, analyst, instrument tune, or digestion batch",
            },
            {
                "Item": "Blank contribution",
                "Result": 12.0,
                "Unit": "% of LOQ response",
                "Rule": "lte",
                "Lower": None,
                "Upper": 20.0,
                "Note": "Reagent, vessel, and digestion blank control",
            },
        ],
    },
    {
        "key": "nitrosamines",
        "label_ko": "니트로사민",
        "label_en": "Nitrosamines",
        "icon": "molecule",
        "tone": "orange",
        "purpose": "Verify highly sensitive trace-level method performance against acceptable intake and product-specific nitrosamine risk.",
        "sample_focus": "Reference concentration should be derived from acceptable intake, maximum daily dose, and sample concentration. Matrix effects, carryover, and isotope/internal standard performance are critical.",
        "ctd": "3.2.P.5.2 / 3.2.P.5.3 / 3.2.P.5.5 / 3.2.P.5.6",
        "basis": "ICH Q2(R2), ICH Q14, ICH M7(R2), health authority nitrosamine guidance",
        "m14": "ICH M14 is useful only as a safety-evidence connection layer when nitrosamine findings must be interpreted against real-world exposure or safety questions; it is not the CMC method validation rule.",
        "prep_defaults": {
            "reference_conc": 0.03,
            "unit": "ng/mL",
            "level_pct": 100.0,
            "weighed_mg": 100.0,
            "purity_pct": 100.0,
            "stock_volume_ml": 100.0,
            "aliquot_ml": 1.0,
            "final_volume_ml": 100.0,
            "dilution_factor": 333.3333,
        },
        "linearity_defaults": {
            "lod": 0.001,
            "loq": 0.003,
            "r2": 0.9988,
            "slope": 42000.0,
            "intercept": 18.0,
            "response_100": 1260.0,
            "response_loq": 126.0,
            "lowest_level_pct": 10.0,
        },
        "rows": [
            {
                "Item": "Matrix interference at RT",
                "Result": 8.0,
                "Unit": "% of LOQ response",
                "Rule": "lte",
                "Lower": None,
                "Upper": 20.0,
                "Note": "Blank, placebo, API, excipient, and extraction solvent selectivity",
            },
            {
                "Item": "LOQ / acceptable intake level",
                "Result": 10.0,
                "Unit": "%",
                "Rule": "lte",
                "Lower": None,
                "Upper": 30.0,
                "Note": "Confirm LOQ is below the concentration derived from AI and maximum daily dose",
            },
            {
                "Item": "Linearity R2",
                "Result": 0.9988,
                "Unit": "",
                "Rule": "gte",
                "Lower": 0.995,
                "Upper": None,
                "Note": "Low ng/mL range; check intercept and weighting model",
            },
            {
                "Item": "Accuracy mean recovery",
                "Result": 88.0,
                "Unit": "%",
                "Rule": "between",
                "Lower": 70.0,
                "Upper": 130.0,
                "Note": "Evaluate near LOQ, AI-derived level, and upper validation level",
            },
            {
                "Item": "Precision RSD",
                "Result": 14.0,
                "Unit": "%",
                "Rule": "lte",
                "Lower": None,
                "Upper": 20.0,
                "Note": "Independent extraction and injection sequence",
            },
            {
                "Item": "Carryover after high standard",
                "Result": 6.0,
                "Unit": "% of LOQ response",
                "Rule": "lte",
                "Lower": None,
                "Upper": 20.0,
                "Note": "Critical for trace nitrosamine LC-MS/GC-MS methods",
            },
        ],
    },
]


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
            "CTD module": "3.2.S",
            "CTD section": "3.2.S.1 General Information",
            "Core question": "Is API identity, nomenclature, structure, salt form, and physicochemical profile defined?",
            "Status": "Partial",
            "Source document": "DMF / API general information / COA",
            "Owner": "API / CMC RA",
            "Risk": "Medium",
            "Next action": "Confirm API form, grade, and product-specific relevance.",
        },
        {
            "CTD module": "3.2.S",
            "CTD section": "3.2.S.2 Manufacture",
            "Core question": "Are API manufacturer, route, critical steps, controls, and change notification traceable?",
            "Status": "Partial",
            "Source document": "DMF S.2 / supplier declaration / quality agreement",
            "Owner": "API supplier / RA",
            "Risk": "High",
            "Next action": "Confirm current DMF version, manufacturing site, and change-control commitment.",
        },
        {
            "CTD module": "3.2.S",
            "CTD section": "3.2.S.3 Characterisation",
            "Core question": "Are API impurities, degradation pathways, polymorph/PSD/water attributes characterized for DP impact?",
            "Status": "Gap",
            "Source document": "DMF S.3 / impurity profile / solid-state report",
            "Owner": "API / Analytical",
            "Risk": "High",
            "Next action": "Bridge impurity, water, PSD, and polymorph information to DP CQA.",
        },
        {
            "CTD module": "3.2.S",
            "CTD section": "3.2.S.4 Control of Drug Substance",
            "Core question": "Do API specifications, methods, validation, batch results, and justification support DP control strategy?",
            "Status": "Partial",
            "Source document": "API specification / COA / method validation / DMF S.4",
            "Owner": "API / QC",
            "Risk": "High",
            "Next action": "Check assay, water, impurities, residual solvents, PSD, and microbiological controls against DP needs.",
        },
        {
            "CTD module": "3.2.S",
            "CTD section": "3.2.S.7 Stability",
            "Core question": "Does API retest period, storage condition, and packaging support DP manufacturing and shelf-life strategy?",
            "Status": "Partial",
            "Source document": "API stability / retest / storage statement",
            "Owner": "API / Stability",
            "Risk": "Medium",
            "Next action": "Confirm API storage and retest coverage for clinical and commercial manufacturing timelines.",
        },
        {
            "CTD module": "3.2.P",
            "CTD section": "3.2.P.1 Description and Composition",
            "Core question": "Is product identity, composition, strength, route, and packaging clearly defined?",
            "Status": "Ready",
            "Source document": "Product composition table / batch formula",
            "Owner": "CMC RA",
            "Risk": "Low",
            "Next action": "Confirm latest formula and packaging version.",
        },
        {
            "CTD module": "3.2.P",
            "CTD section": "3.2.P.2 Pharmaceutical Development",
            "Core question": "Does development rationale support QTPP, CQA, formulation, and process choices?",
            "Status": "Partial",
            "Source document": "Development report / comparative dissolution or IVR report",
            "Owner": "Formulation",
            "Risk": "Medium",
            "Next action": "Link CQA to specification and stability controls.",
        },
        {
            "CTD module": "3.2.P",
            "CTD section": "3.2.P.3 Manufacture",
            "Core question": "Can the commercial process and IPC strategy consistently produce target quality?",
            "Status": "Partial",
            "Source document": "MFR / process flow / PV protocol",
            "Owner": "Manufacturing",
            "Risk": "Medium",
            "Next action": "Add CPP-CQA connection and process validation status.",
        },
        {
            "CTD module": "3.2.P",
            "CTD section": "3.2.P.4 Control of Excipients",
            "Core question": "Are excipient standards, supplier controls, and novel excipient risks covered?",
            "Status": "Ready",
            "Source document": "Excipient COA / pharmacopeial standard",
            "Owner": "QC",
            "Risk": "Low",
            "Next action": "Confirm supplier qualification evidence.",
        },
        {
            "CTD module": "3.2.P",
            "CTD section": "3.2.P.5 Control of Drug Product",
            "Core question": "Do specifications, methods, validation, and batch data support release and shelf-life quality?",
            "Status": "Gap",
            "Source document": "Specification / method validation / batch analysis",
            "Owner": "Analytical",
            "Risk": "High",
            "Next action": "Complete P.5.6 rationale and validation gate review.",
        },
        {
            "CTD module": "3.2.P",
            "CTD section": "3.2.P.6 Reference Standards",
            "Core question": "Are reference standards qualified for assay, identity, and impurity testing?",
            "Status": "Partial",
            "Source document": "Reference standard COA / qualification report",
            "Owner": "QC",
            "Risk": "Medium",
            "Next action": "Confirm purity, water, storage, retest, and use history.",
        },
        {
            "CTD module": "3.2.P",
            "CTD section": "3.2.P.7 Container Closure System",
            "Core question": "Does container closure evidence support compatibility, protection, and use?",
            "Status": "Partial",
            "Source document": "CCS specification / E&L / CCI",
            "Owner": "Packaging",
            "Risk": "Medium",
            "Next action": "Connect packaging evidence to P.2.4 and P.8 stability.",
        },
        {
            "CTD module": "3.2.P",
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


def default_dmf_source_rows() -> list[dict[str, Any]]:
    return [
        {
            "DMF section": "Administrative access / LoA",
            "Expected information": "DMF number, holder, LoA, current version, amendment history",
            "Document source": "LoA / DMF holder letter",
            "Document text / excerpt": "",
            "Confirmed value": "LoA received; version not yet confirmed",
            "DP linkage": "Supports applicant right of reference and CTD 3.2.S cross-reference",
            "Status": "Partial",
            "Risk": "High",
            "Action": "Confirm current DMF version and holder commitment before relying on the package.",
        },
        {
            "DMF section": "S.1 API identity and grade",
            "Expected information": "API name, salt form, grade, physical form, key physicochemical attributes",
            "Document source": "DMF S.1 / API specification / COA",
            "Document text / excerpt": "",
            "Confirmed value": "Naltrexone API identity assumed; grade to confirm",
            "DP linkage": "Defines the drug substance used in formula, assay basis, and clinical material bridge",
            "Status": "Partial",
            "Risk": "Medium",
            "Action": "Confirm API form, grade, and material sameness for clinical and commercial use.",
        },
        {
            "DMF section": "S.2 Manufacture / supplier control",
            "Expected information": "Manufacturer, manufacturing site, critical route controls, quality agreement, change notification",
            "Document source": "DMF S.2 / supplier qualification file",
            "Document text / excerpt": "",
            "Confirmed value": "Supplier status not fully documented",
            "DP linkage": "Affects starting material control, impurity risk, and post-change comparability planning",
            "Status": "Gap",
            "Risk": "High",
            "Action": "Request supplier qualification and change-notification commitment.",
        },
        {
            "DMF section": "S.3 Characterisation / impurity profile",
            "Expected information": "Specified/unspecified impurities, degradation pathway, residual solvents, structural alerts if applicable",
            "Document source": "DMF S.3 / impurity report / COA trend",
            "Document text / excerpt": "",
            "Confirmed value": "API impurity and DP degradant distinction needs mapping",
            "DP linkage": "Feeds DP related substances, stability trend, ICH M7/Q3B rationale",
            "Status": "Partial",
            "Risk": "High",
            "Action": "Separate API impurity carryover from DP degradation products.",
        },
        {
            "DMF section": "S.4 API specification and methods",
            "Expected information": "Assay, water, impurities, residual solvents, PSD, polymorph, microbial limits if applicable",
            "Document source": "API specification / method / validation / COA",
            "Document text / excerpt": "",
            "Confirmed value": "API specification available; method/version traceability to confirm",
            "DP linkage": "Supports DP formula, assay correction, processability, release, and stability controls",
            "Status": "Partial",
            "Risk": "High",
            "Action": "Trace each API criterion to DP CQA and analytical calculation impact.",
        },
        {
            "DMF section": "S.7 API stability / retest",
            "Expected information": "Retest period, storage condition, container, excursion handling, ongoing stability",
            "Document source": "API stability report / retest statement",
            "Document text / excerpt": "",
            "Confirmed value": "Retest and storage statement to confirm",
            "DP linkage": "Supports manufacturing hold time, clinical material usage, and DP shelf-life strategy",
            "Status": "Partial",
            "Risk": "Medium",
            "Action": "Confirm API retest coverage for the intended manufacturing and clinical timeline.",
        },
    ]


def default_ctd_document_rows() -> list[dict[str, Any]]:
    return [
        {
            "CTD module": "3.2.S",
            "CTD part": "3.2.S.1 General Information",
            "Expected information": "Nomenclature, structure, general properties, salt/form/grade",
            "Document source": "DMF S.1 / API general information",
            "Document text / excerpt": "",
            "Confirmed value": "API identity and form require confirmation",
            "Evidence use": "API identity anchor for formula, assay, and DMF bridge",
            "Status": "Partial",
            "Risk": "Medium",
            "Owner": "API / CMC RA",
            "Next action": "Confirm API form and grade against clinical/commercial material.",
        },
        {
            "CTD module": "3.2.S",
            "CTD part": "3.2.S.2 Manufacture",
            "Expected information": "Manufacturer, process description, controls of materials, critical steps, process controls",
            "Document source": "DMF S.2 / supplier statement",
            "Document text / excerpt": "",
            "Confirmed value": "Manufacturing site and current process version need confirmation",
            "Evidence use": "Supplier/change-control risk and API process impurity context",
            "Status": "Gap",
            "Risk": "High",
            "Owner": "API supplier / RA",
            "Next action": "Request current DMF version, LoA, site, and change notification basis.",
        },
        {
            "CTD module": "3.2.S",
            "CTD part": "3.2.S.3 Characterisation",
            "Expected information": "Structure elucidation, impurities, degradation products, polymorph/PSD/water if product-relevant",
            "Document source": "DMF S.3 / characterization package",
            "Document text / excerpt": "",
            "Confirmed value": "Impurity and solid-state bridge not yet complete",
            "Evidence use": "Links API attributes to DP CQA, P.5.5, P.5.6, and P.8",
            "Status": "Gap",
            "Risk": "High",
            "Owner": "API / Analytical",
            "Next action": "Map API impurities, water, PSD, and polymorph to DP control strategy.",
        },
        {
            "CTD module": "3.2.S",
            "CTD part": "3.2.S.4 Control of Drug Substance",
            "Expected information": "API specification, analytical methods, validation, batch analysis, justification",
            "Document source": "DMF S.4 / API specification / COA",
            "Document text / excerpt": "",
            "Confirmed value": "API specification exists; DP impact needs traceability",
            "Evidence use": "Supports API-to-DP bridge, assay basis, impurity limits, and processability",
            "Status": "Partial",
            "Risk": "High",
            "Owner": "API / QC",
            "Next action": "Compare API criteria against DP CQA and validation calculations.",
        },
        {
            "CTD module": "3.2.S",
            "CTD part": "3.2.S.7 Stability",
            "Expected information": "API stability, retest period, storage, packaging, commitment",
            "Document source": "API stability / retest package",
            "Document text / excerpt": "",
            "Confirmed value": "API retest support to confirm",
            "Evidence use": "Supports clinical material use period and DP manufacturing timeline",
            "Status": "Partial",
            "Risk": "Medium",
            "Owner": "API / Stability",
            "Next action": "Confirm retest coverage and storage compatibility with DP manufacturing.",
        },
        {
            "CTD module": "3.2.P",
            "CTD part": "3.2.P.1 Description and Composition",
            "Expected information": "Product description, composition, strength, route, container closure, batch formula",
            "Document source": "Formula / composition table / product profile",
            "Document text / excerpt": "",
            "Confirmed value": "Naltrexone PLGA depot injection; composition details to confirm",
            "Evidence use": "Defines target product and connects all downstream P sections",
            "Status": "Ready",
            "Risk": "Low",
            "Owner": "CMC RA",
            "Next action": "Confirm latest formula, batch size, and clinical/commercial sameness.",
        },
        {
            "CTD module": "3.2.P",
            "CTD part": "3.2.P.2 Pharmaceutical Development",
            "Expected information": "QTPP, CQA, excipient selection, formulation/process rationale, clinical-to-commercial bridge",
            "Document source": "Development report / QbD report / IVR or dissolution package",
            "Document text / excerpt": "",
            "Confirmed value": "PLGA long-acting formulation rationale needs source mapping",
            "Evidence use": "Connects early CMC decisions to clinical material and final product design",
            "Status": "Partial",
            "Risk": "High",
            "Owner": "Formulation / CMC RA",
            "Next action": "Map formulation variables, PLGA grade, CQA, and release profile to specification.",
        },
        {
            "CTD module": "3.2.P",
            "CTD part": "3.2.P.3 Manufacture",
            "Expected information": "Manufacturer, batch formula, process flow, critical steps, IPC, scale, process validation strategy",
            "Document source": "MFR / process flow / batch records / PV plan",
            "Document text / excerpt": "",
            "Confirmed value": "Manufacturing flow and CPP-CQA linkage need confirmation",
            "Evidence use": "Supports manufacturability, clinical batch representativeness, and change-risk control",
            "Status": "Partial",
            "Risk": "High",
            "Owner": "Manufacturing",
            "Next action": "Capture process parameters, IPCs, hold times, scale-up assumptions, and batch genealogy.",
        },
        {
            "CTD module": "3.2.P",
            "CTD part": "3.2.P.5 Control of Drug Product",
            "Expected information": "Specification, analytical procedures, validation, batch analysis, impurities, specification rationale",
            "Document source": "DP specification / methods / validation / batch analysis",
            "Document text / excerpt": "",
            "Confirmed value": "P.5.6 rationale and validation range need review",
            "Evidence use": "Main reviewer-facing control strategy and acceptance-criterion rationale",
            "Status": "Gap",
            "Risk": "High",
            "Owner": "Analytical / CMC RA",
            "Next action": "Complete specification rationale, validation gate, calculation check, and batch/stability linkage.",
        },
        {
            "CTD module": "3.2.P",
            "CTD part": "3.2.P.8 Stability",
            "Expected information": "Stability summary, protocol, trend data, shelf-life, storage, commitments",
            "Document source": "Stability report / trend table / protocol",
            "Document text / excerpt": "",
            "Confirmed value": "Shelf-life support not yet complete",
            "Evidence use": "Supports release/stability criteria, impurity limits, storage, and clinical/commercial bridge",
            "Status": "Gap",
            "Risk": "High",
            "Owner": "Stability / CMC RA",
            "Next action": "Add trend table, release-profile drift review, degradation risk, and commitment plan.",
        },
        {
            "CTD module": "Other CTD",
            "CTD part": "Module 1 Regional / Administrative",
            "Expected information": "Application forms, labels, regional quality forms, cover letters, local requirements",
            "Document source": "Regional submission package",
            "Document text / excerpt": "",
            "Confirmed value": "Regional requirements not yet mapped",
            "Evidence use": "Defines local submission expectations and labeling/quality commitments",
            "Status": "Partial",
            "Risk": "Medium",
            "Owner": "RA",
            "Next action": "Map MFDS/FDA/EMA regional requirements to Module 3 evidence needs.",
        },
        {
            "CTD module": "Other CTD",
            "CTD part": "Module 2.3 Quality Overall Summary",
            "Expected information": "Quality narrative integrating 3.2.S, 3.2.P, critical risks, and justification",
            "Document source": "QOS draft / quality summary",
            "Document text / excerpt": "",
            "Confirmed value": "QOS should be generated after S/P evidence map is stable",
            "Evidence use": "Executive-quality bridge from detailed CMC data to reviewer narrative",
            "Status": "Gap",
            "Risk": "High",
            "Owner": "CMC RA writer",
            "Next action": "Generate QOS only after source evidence, calculations, and P.5.6 rationale are aligned.",
        },
        {
            "CTD module": "Other CTD",
            "CTD part": "Module 2.5 / 2.7 Clinical Overview and Summaries",
            "Expected information": "Clinical exposure, dose, safety/efficacy context, clinical batch linkage if relevant",
            "Document source": "Clinical overview / study summary / protocol",
            "Document text / excerpt": "",
            "Confirmed value": "Clinical material representativeness needs CMC bridge note",
            "Evidence use": "Context for clinical material and major CMC change impact",
            "Status": "Partial",
            "Risk": "Medium",
            "Owner": "Clinical / RA / CMC",
            "Next action": "Capture which clinical batches and quality attributes support the proposed product.",
        },
        {
            "CTD module": "Other CTD",
            "CTD part": "Module 4 / 5 Nonclinical and Clinical Reports",
            "Expected information": "Nonclinical/clinical reports affected by formulation, impurity, route, or exposure changes",
            "Document source": "Study reports / clinical study reports",
            "Document text / excerpt": "",
            "Confirmed value": "Only CMC-change-relevant context should be captured here",
            "Evidence use": "Flags whether CMC changes may require bridging, additional justification, or expert review",
            "Status": "Partial",
            "Risk": "Medium",
            "Owner": "Nonclinical / Clinical / RA",
            "Next action": "Do not replace Module 4/5 review; capture links that affect CMC decision risk.",
        },
    ]


def default_document_logic_rows() -> list[dict[str, Any]]:
    return [
        {
            "Review stage": "Product profile / scope setting",
            "Input document": "Project charter, target product profile, route, strength, region strategy",
            "What to capture": "Active substance, formulation platform, route, clinical material, target regions, lifecycle stage",
            "Where to apply": "Dashboard / document request list / CTD scope",
            "Decision point": "Which CTD modules and CMC documents are actually needed for this product?",
            "CMC risk if unclear": "Documents may be reviewed without the product context needed to judge formulation, process, specification, and regional expectations.",
            "Output artifact": "Product-profile-driven review prompts",
            "Status": "Partial",
            "Risk": "Medium",
            "Action": "Confirm product profile before judging document sufficiency.",
        },
        {
            "Review stage": "Raw material / DMF intake",
            "Input document": "LoA, DMF holder letter, API specification, COA, impurity report, retest statement",
            "What to capture": "DMF version, API form/grade, potency or water correction, impurities, PSD/polymorph if relevant, storage/retest, supplier change control",
            "Where to apply": "3.2.S / DMF-to-DP bridge / P.1 formula / P.5 control strategy",
            "Decision point": "Does the API package support the drug product formula, clinical material, and final quality strategy?",
            "CMC risk if unclear": "A wrong raw-material assumption can affect formula calculation, impurity limits, release profile, stability, and later comparability arguments.",
            "Output artifact": "DMF-to-DP bridge and API evidence request list",
            "Status": "Gap",
            "Risk": "High",
            "Action": "Request source text and confirmed values for API identity, grade, specification, impurity, and retest controls.",
        },
        {
            "Review stage": "Formulation development",
            "Input document": "P.2 development report, QTPP/CQA table, excipient rationale, PLGA grade rationale, IVR/release development data",
            "What to capture": "Formulation variables, PLGA attributes, release mechanism, CQA linkage, clinical-to-commercial formulation bridge",
            "Where to apply": "3.2.P.2 / 3.2.P.5.6 / Module 2.3",
            "Decision point": "Can the selected formulation be defended as clinically relevant and commercially reproducible?",
            "CMC risk if unclear": "A late formulation change can become a comparability, stability, nonclinical, clinical, or reviewer-question issue.",
            "Output artifact": "P.2 evidence map and formulation-risk memo",
            "Status": "Partial",
            "Risk": "High",
            "Action": "Link formulation variables to release, stability, manufacturability, and specification rationale.",
        },
        {
            "Review stage": "Manufacturing process",
            "Input document": "MFR, process flow, batch record, IPC table, sterilization or aseptic strategy, hold-time data, scale-up plan",
            "What to capture": "Batch genealogy, process steps, CPP, IPC, equipment/scale, hold time, in-process acceptance criteria, process validation assumptions",
            "Where to apply": "3.2.P.3 / 3.2.P.5 / 3.2.P.8",
            "Decision point": "Do process controls explain and protect the critical quality attributes?",
            "CMC risk if unclear": "Process or scale changes may alter particle attributes, release, residual solvent, sterility assurance, or stability trend.",
            "Output artifact": "Manufacturing control and clinical-batch representativeness note",
            "Status": "Partial",
            "Risk": "High",
            "Action": "Trace each critical step to CQA, IPC, batch analysis, and stability evidence.",
        },
        {
            "Review stage": "Specification and analytical control",
            "Input document": "DP specification, analytical method, method validation, batch analysis, impurity qualification, calculation sheet",
            "What to capture": "Acceptance criteria, method range, LOD/LOQ, specificity, recovery, precision, system suitability, batch/stability basis, calculation formula",
            "Where to apply": "3.2.P.5.1 / 3.2.P.5.2 / 3.2.P.5.3 / 3.2.P.5.4 / 3.2.P.5.5 / 3.2.P.5.6",
            "Decision point": "Is each quality criterion supported by data, validated method capability, safety or performance relevance, and batch/stability history?",
            "CMC risk if unclear": "Unsupported limits or calculation errors can make the specification indefensible even when the table itself looks complete.",
            "Output artifact": "P.5.6 rationale and calculation/validation review memo",
            "Status": "Gap",
            "Risk": "High",
            "Action": "Convert every missing rationale into a reviewer question and evidence request.",
        },
        {
            "Review stage": "Stability and shelf-life",
            "Input document": "Stability protocol, long-term/accelerated data, trend table, release-profile trend, degradation evaluation, shelf-life proposal",
            "What to capture": "Storage condition, time points, batch coverage, trend, excursions, impurity growth, release drift, proposed shelf-life and commitments",
            "Where to apply": "3.2.P.8 / 3.2.P.5.6 / Module 2.3",
            "Decision point": "Does the stability package support the proposed shelf-life and the selected release/stability specification?",
            "CMC risk if unclear": "Late stability drift can force shelf-life reduction, specification revision, additional batches, or agency questions.",
            "Output artifact": "Stability evidence and commitment map",
            "Status": "Gap",
            "Risk": "High",
            "Action": "Connect trend evidence to acceptance criteria, degradation risk, and shelf-life justification.",
        },
        {
            "Review stage": "Clinical material bridge",
            "Input document": "Clinical batch records, clinical protocol, clinical overview, dose/exposure summary, comparability or bridging memo",
            "What to capture": "Which batches were dosed, whether formula/process/specification match the proposed product, and which CMC changes occurred after dosing",
            "Where to apply": "3.2.P.2 / 3.2.P.3 / Module 2.5 / Module 5",
            "Decision point": "Can the clinical trial material represent the proposed commercial drug product?",
            "CMC risk if unclear": "A major CMC difference can trigger bridging, comparability justification, additional stability, nonclinical, clinical, or regulatory review needs.",
            "Output artifact": "Clinical-material representativeness memo",
            "Status": "Partial",
            "Risk": "High",
            "Action": "List each post-clinical CMC difference and define the needed bridge evidence.",
        },
        {
            "Review stage": "Regional submission / response",
            "Input document": "Module 1 forms, regional quality requirements, QOS, labels, deficiency letter, agency meeting questions",
            "What to capture": "Regional commitments, CTD placement, label-quality linkage, requested clarification, response owner, evidence deadline",
            "Where to apply": "Module 1 / Module 2.3 / Module 3 / CMC RA response memo",
            "Decision point": "Where should the answer live in CTD, and which source evidence makes it defensible?",
            "CMC risk if unclear": "A response can sound plausible but fail because it is not anchored to the correct CTD section or source document.",
            "Output artifact": "CMC RA response memo and CTD update action table",
            "Status": "Partial",
            "Risk": "Medium",
            "Action": "Write responses only after the source evidence, CTD location, and owner are traceable.",
        },
    ]


def default_validation_rows() -> list[dict[str, Any]]:
    return validation_rows_for_item("assay")


def validation_profile(key: str) -> dict[str, Any]:
    for profile in VALIDATION_TEST_ITEMS:
        if profile["key"] == key:
            return profile
    return VALIDATION_TEST_ITEMS[0]


def validation_item_label(profile: dict[str, Any], lang: str = "ko") -> str:
    if lang == "en":
        return str(profile["label_en"])
    return str(profile["label_ko"])


def validation_rows_for_item(key: str) -> list[dict[str, Any]]:
    profile = validation_profile(key)
    return [dict(row) for row in profile["rows"]]


def default_validation_item_tables() -> dict[str, pd.DataFrame]:
    return {str(profile["key"]): pd.DataFrame(validation_rows_for_item(str(profile["key"]))) for profile in VALIDATION_TEST_ITEMS}


def infer_ctd_module(section: Any) -> str:
    text = str(section)
    if "3.2.S" in text:
        return "3.2.S"
    if "3.2.P" in text:
        return "3.2.P"
    return "Other CTD"


def ensure_state_frame(key: str, default_rows: list[dict[str, Any]]) -> None:
    default = pd.DataFrame(default_rows)
    if key not in st.session_state:
        st.session_state[key] = default
        return

    current = st.session_state[key].copy()
    for column in default.columns:
        if column not in current.columns:
            if column == "CTD module" and "CTD section" in current.columns:
                current[column] = current["CTD section"].apply(infer_ctd_module)
            elif column == "CTD module" and "CTD part" in current.columns:
                current[column] = current["CTD part"].apply(infer_ctd_module)
            else:
                current[column] = ""
    ordered = [column for column in default.columns if column in current.columns]
    extras = [column for column in current.columns if column not in ordered]
    st.session_state[key] = current[ordered + extras]


def ensure_validation_item_tables() -> dict[str, pd.DataFrame]:
    if "validation_items" not in st.session_state:
        st.session_state.validation_items = default_validation_item_tables()
    tables = st.session_state.validation_items
    for profile in VALIDATION_TEST_ITEMS:
        key = str(profile["key"])
        if key not in tables:
            tables[key] = pd.DataFrame(validation_rows_for_item(key))
    return tables


def validation_review_frame(include_gate: bool = True) -> pd.DataFrame:
    tables = ensure_validation_item_tables()
    frames: list[pd.DataFrame] = []
    for profile in VALIDATION_TEST_ITEMS:
        key = str(profile["key"])
        df = tables.get(key, pd.DataFrame(validation_rows_for_item(key))).copy()
        df = df.drop(columns=["Gate"], errors="ignore")
        df.insert(0, "Test item", validation_item_label(profile, "en"))
        df["CTD update"] = profile["ctd"]
        df["Regulatory basis"] = profile["basis"]
        if include_gate:
            df["Gate"] = df.apply(evaluate_rule, axis=1)
        frames.append(df)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def validation_summary_frame() -> pd.DataFrame:
    tables = ensure_validation_item_tables()
    rows: list[dict[str, Any]] = []
    for profile in VALIDATION_TEST_ITEMS:
        key = str(profile["key"])
        df = tables.get(key, pd.DataFrame(validation_rows_for_item(key))).copy()
        df["Gate"] = df.apply(evaluate_rule, axis=1)
        review_count = int((df["Gate"] == "Review").sum())
        info_count = int((df["Gate"] == "Info").sum())
        rows.append(
            {
                "Test item": validation_item_label(profile, "en"),
                "Gate": "Review" if review_count else "Pass",
                "Review items": review_count,
                "Info items": info_count,
                "Result rows": int(len(df)),
                "Regulatory basis": profile["basis"],
                "CTD update": profile["ctd"],
            }
        )
    return pd.DataFrame(rows)


def initialize_state() -> None:
    defaults = {
        "intake_df": pd.DataFrame(default_intake_rows()),
        "evidence_df": pd.DataFrame(default_evidence_rows()),
        "spec_df": pd.DataFrame(default_spec_rows()),
        "dmf_df": pd.DataFrame(default_dmf_rows()),
        "dmf_source_df": pd.DataFrame(default_dmf_source_rows()),
        "ctd_document_df": pd.DataFrame(default_ctd_document_rows()),
        "document_logic_df": pd.DataFrame(default_document_logic_rows()),
        "document_notes": {"dmf": "", "ctd_s": "", "ctd_p": "", "ctd_other": ""},
        "validation_df": pd.DataFrame(default_validation_rows()),
        "validation_test_item": "assay",
        "validation_items": default_validation_item_tables(),
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    ensure_state_frame("intake_df", default_intake_rows())
    ensure_state_frame("evidence_df", default_evidence_rows())
    ensure_state_frame("spec_df", default_spec_rows())
    ensure_state_frame("dmf_df", default_dmf_rows())
    ensure_state_frame("dmf_source_df", default_dmf_source_rows())
    ensure_state_frame("ctd_document_df", default_ctd_document_rows())
    ensure_state_frame("document_logic_df", default_document_logic_rows())
    ensure_validation_item_tables()


def tr(lang: str, key: str) -> str:
    return TEXT.get(lang, TEXT["ko"]).get(key, key)


def localize_value(value: Any, lang: str) -> Any:
    if lang != "ko" or not isinstance(value, str):
        return value
    return VALUE_KO.get(value, value)


def delocalize_value(value: Any, lang: str) -> Any:
    if lang != "ko" or not isinstance(value, str):
        return value
    return KO_TO_VALUE.get(value, value)


def option_labels(options: list[str], lang: str) -> list[str]:
    return [str(localize_value(option, lang)) for option in options]


def localize_content_value(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    if value in CONTENT_KO:
        return CONTENT_KO[value]
    if value.startswith("Please provide source text and confirmed value for ") and value.endswith("."):
        target = value.removeprefix("Please provide source text and confirmed value for ").removesuffix(".")
        return f"{target}에 대한 원문 발췌와 확인값을 제공/확인하세요."
    if value.startswith("Please provide source evidence and confirmed value for ") and value.endswith("."):
        target = value.removeprefix("Please provide source evidence and confirmed value for ").removesuffix(".")
        return f"{target}에 대한 원문 근거와 확인값을 제공/확인하세요."
    if value.startswith("Please justify missing or incomplete evidence for ") and value.endswith("."):
        target = value.removeprefix("Please justify missing or incomplete evidence for ").removesuffix(".")
        return f"{target}의 누락 또는 불완전 근거를 설명하세요."
    if value.startswith("Please justify the acceptance criterion for ") and value.endswith("."):
        target = value.removeprefix("Please justify the acceptance criterion for ").removesuffix(".")
        return f"{target} 허용기준의 설정 근거를 설명하세요."
    if value.startswith("Please explain how ") and value.endswith(" supports the drug product control strategy."):
        target = value.removeprefix("Please explain how ").removesuffix(" supports the drug product control strategy.")
        return f"{target}가 완제 관리전략을 어떻게 지지하는지 설명하세요."
    if value.startswith("Please provide raw data and sample-preparation rationale for ") and value.endswith("."):
        target = value.removeprefix("Please provide raw data and sample-preparation rationale for ").removesuffix(".")
        return f"{target}에 대한 raw data와 시료 제조 근거를 제공하세요."
    if value.startswith("Client intake: "):
        return value.replace("Client intake:", "고객 문서 접수:").replace("High risk", "고위험").replace("Medium risk", "중간 리스크").replace("Low risk", "낮은 리스크")
    if value.startswith("DMF source input: "):
        return value.replace("DMF source input:", "DMF 원문 입력:").replace("High risk", "고위험").replace("Medium risk", "중간 리스크").replace("Low risk", "낮은 리스크")
    if value.startswith("CTD document input: "):
        return value.replace("CTD document input:", "CTD 문서 입력:").replace("High risk", "고위험").replace("Medium risk", "중간 리스크").replace("Low risk", "낮은 리스크")
    if value.startswith("Validation gate review: "):
        return value.replace("Validation gate review:", "밸리데이션 Gate 검토:").replace("rule", "판정 규칙")
    return value


def localize_dataframe(df: pd.DataFrame, lang: str) -> pd.DataFrame:
    if lang != "ko":
        return df.copy()
    localized = df.copy()
    localized = localized.replace(VALUE_KO)
    for column in BODY_TRANSLATION_COLUMNS:
        if column in localized.columns:
            localized[column] = localized[column].map(localize_content_value)
    localized = localized.rename(columns=COLUMN_KO)
    return localized


def delocalize_dataframe(df: pd.DataFrame, lang: str) -> pd.DataFrame:
    if lang != "ko":
        return df.copy()
    internal = df.copy()
    internal = internal.rename(columns=KO_TO_COLUMN)
    for column in BODY_TRANSLATION_COLUMNS:
        if column in internal.columns:
            internal[column] = internal[column].map(
                lambda value: KO_TO_CONTENT.get(value, value) if isinstance(value, str) else value
            )
    internal = internal.replace(KO_TO_VALUE)
    return internal


def display_dataframe(df: pd.DataFrame, lang: str, columns: list[str] | None = None) -> pd.DataFrame:
    if columns:
        existing_columns = [column for column in columns if column in df.columns]
        view = df[existing_columns].copy()
    else:
        view = df.copy()
    return localize_dataframe(view, lang)


def table_columns(lang: str, columns: list[str]) -> list[str]:
    if lang != "ko":
        return columns
    return [COLUMN_KO.get(column, column) for column in columns]


def profile_copy(profile: dict[str, Any], field: str, lang: str) -> str:
    if lang == "ko":
        translated = PROFILE_COPY_KO.get(str(profile.get("key", "")), {}).get(field)
        if not translated and field == "focus":
            translated = PROFILE_COPY_KO.get(str(profile.get("key", "")), {}).get("sample_focus")
        if translated:
            return translated
    return str(profile.get(field, ""))


def localize_note(text: str, lang: str) -> str:
    if lang != "ko":
        return text
    replacements = {
        "Sample prep gate: Pass. Blank or zero-level preparation has no analyte concentration.": "시료 제조 Gate: 통과. Blank 또는 0% level 제조로 분석대상 농도가 없습니다.",
        "Sample prep gate: Hold. Target concentration is zero, but the prepared solution contains analyte.": "시료 제조 Gate: 보류. 목표 농도는 0이지만 제조액에 분석대상이 포함되어 있습니다.",
        "Sample prep gate: Pass. Actual theoretical concentration is close to target.": "시료 제조 Gate: 통과. 실제 이론농도가 목표농도와 잘 맞습니다.",
        "Sample prep gate: Review. Check weighing, purity correction, volume, and dilution factor.": "시료 제조 Gate: 검토. 칭량량, 순도 보정, 부피, 희석배수를 확인하세요.",
        "Sample prep gate: Hold. The prepared concentration does not support the target validation level.": "시료 제조 Gate: 보류. 제조 농도가 목표 밸리데이션 level을 지지하지 못합니다.",
        "Linearity R2 is below 0.99. Regression suitability is high risk.": "직선성 R2가 0.99 미만입니다. 회귀식 적합성이 고위험입니다.",
        "Intercept is greater than 2% of the 100% response. Check blank, impurity/water contribution, and calibration range.": "Intercept가 100% response의 2%를 초과합니다. Blank, 불순물/수분 영향, 검량선 범위를 확인하세요.",
        "Intercept is greater than 5% of the LOQ response. Low-level validation can be biased even when R2 is high.": "Intercept가 LOQ response의 5%를 초과합니다. R2가 높아도 저농도 밸리데이션에 bias가 생길 수 있습니다.",
        "LOQ is higher than the lowest linearity level. Recheck range design.": "LOQ가 가장 낮은 직선성 level보다 높습니다. Range 설계를 다시 확인하세요.",
        "LOD/LOQ and intercept risk are acceptable for the current reference concentration.": "현재 기준농도에서 LOD/LOQ와 intercept 리스크는 허용 가능한 수준입니다.",
        "Run Calculation / Validation tab to generate LOD/LOQ and intercept notes.": "계산 / 밸리데이션 탭을 실행하면 LOD/LOQ와 intercept note가 생성됩니다.",
    }
    return replacements.get(text, text)


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


def score_document_inputs(df: pd.DataFrame) -> float:
    if df.empty or "Status" not in df.columns:
        return 0.0
    status_weights = {"Ready": 1.0, "Partial": 0.55, "Gap": 0.0, "N/A": 0.7}
    risk_weights = {"Low": 1.0, "Medium": 0.65, "High": 0.25}
    scores = []
    for _, row in df.iterrows():
        status_score = status_weights.get(str(row.get("Status", "")), 0.0)
        risk_score = risk_weights.get(str(row.get("Risk", "")), 0.5)
        text = str(row.get("Document text / excerpt", "")).strip()
        value = str(row.get("Confirmed value", "")).strip()
        source_score = 1.0 if text else 0.7 if value else 0.35
        scores.append((status_score * 0.45) + (risk_score * 0.25) + (source_score * 0.30))
    return round(float(sum(scores) / len(scores) * 100), 1)


def source_text_count(*frames: pd.DataFrame) -> int:
    count = 0
    for frame in frames:
        if "Document text / excerpt" in frame.columns:
            count += int(frame["Document text / excerpt"].fillna("").astype(str).str.strip().ne("").sum())
    notes = st.session_state.get("document_notes", {})
    if isinstance(notes, dict):
        count += sum(1 for value in notes.values() if str(value).strip())
    return count


def document_gap_frame() -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    if "ctd_document_df" in st.session_state:
        ctd = st.session_state.ctd_document_df.copy()
        ctd["Document group"] = ctd["CTD module"]
        ctd["Expected client document"] = ctd["Document source"]
        ctd["Client question"] = ctd.apply(
            lambda row: f"Please provide or clarify source evidence for {row['CTD part']}.",
            axis=1,
        )
        ctd["CTD update direction"] = ctd["CTD part"]
        frames.append(ctd[["Document group", "CTD part", "Client question", "Expected client document", "Risk", "Status", "CTD update direction"]])
    if "dmf_source_df" in st.session_state:
        dmf = st.session_state.dmf_source_df.copy()
        dmf["Document group"] = "DMF"
        dmf["CTD part"] = dmf["DMF section"]
        dmf["Expected client document"] = dmf["Document source"]
        dmf["Client question"] = dmf.apply(
            lambda row: f"Please provide or clarify the DMF source text for {row['DMF section']}.",
            axis=1,
        )
        dmf["CTD update direction"] = dmf["DP linkage"]
        frames.append(dmf[["Document group", "CTD part", "Client question", "Expected client document", "Risk", "Status", "CTD update direction"]])
    if not frames:
        return pd.DataFrame()
    combined = pd.concat(frames, ignore_index=True)
    return combined[(combined["Risk"].isin(["High", "Medium"])) | (combined["Status"].isin(["Partial", "Gap"]))]


def product_profile_prompts(profile: dict[str, Any]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Profile signal": profile["active_substance"],
                "Evidence impact": "API identity, grade, salt/form, potency/water correction, impurity carryover",
                "CTD section": "3.2.S.1 / 3.2.S.4 / 3.2.P.1 / 3.2.P.5",
                "Risk question": "Is the API used for clinical material the same material strategy intended for the final DP?",
            },
            {
                "Profile signal": profile["api_supplier"],
                "Evidence impact": "DMF access, supplier qualification, change notification, manufacturing-site traceability",
                "CTD section": "3.2.S.2 / 3.2.S.4 / 3.2.P DMF bridge",
                "Risk question": "Can the applicant defend the current DMF version and supplier commitment?",
            },
            {
                "Profile signal": profile["formulation_platform"],
                "Evidence impact": "QTPP/CQA, formulation variables, process design, release profile, manufacturability",
                "CTD section": "3.2.P.2 / 3.2.P.3 / 3.2.P.5.6",
                "Risk question": "Does the formulation platform remain bridgeable from clinical to commercial product?",
            },
            {
                "Profile signal": profile["clinical_material"],
                "Evidence impact": "Clinical batch genealogy, representativeness, comparability, bridging risk",
                "CTD section": "3.2.P.2 / 3.2.P.3 / Module 2.5 / Module 5",
                "Risk question": "Can the clinical trial material be justified as representative of the proposed commercial product?",
            },
            {
                "Profile signal": profile["target_regions"],
                "Evidence impact": "Regional Module 1 expectations, QOS narrative, CTD placement, agency response style",
                "CTD section": "Module 1 / Module 2.3 / 3.2.S / 3.2.P",
                "Risk question": "Which regional requirements change the evidence package or CTD update location?",
            },
        ]
    )


def document_priority(risk: Any, status: Any) -> str:
    risk_text = str(risk)
    status_text = str(status)
    if risk_text == "High" and status_text in {"Gap", "Partial"}:
        return "Critical"
    if risk_text == "High" or status_text == "Gap":
        return "Watch"
    if risk_text == "Medium" or status_text == "Partial":
        return "Watch"
    return "Info"


def document_decision_points(profile: dict[str, Any]) -> pd.DataFrame:
    rows: list[dict[str, str]] = [
        {
            "Priority": "Watch",
            "Source area": "Product profile",
            "Source item": str(profile["product"]),
            "Key point": (
                f"{profile['active_substance']} / {profile['formulation_platform']} / "
                f"{profile['route']} / {profile['target_regions']}"
            ),
            "Why it matters": "The product profile determines which DMF and CTD evidence is applicable.",
            "Evidence required": "Project scope, target product profile, target region, clinical material strategy",
            "Affected CTD": "Module 1 / Module 2.3 / 3.2.S / 3.2.P",
            "Suggested action": "Use the profile to decide document request scope before judging sufficiency.",
            "User decision": "Open",
        }
    ]

    dmf_source = st.session_state.get("dmf_source_df", pd.DataFrame()).copy()
    if not dmf_source.empty:
        focus = dmf_source[
            dmf_source.get("Risk", pd.Series(dtype=str)).isin(["High", "Medium"])
            | dmf_source.get("Status", pd.Series(dtype=str)).isin(["Gap", "Partial"])
        ]
        for _, row in focus.iterrows():
            rows.append(
                {
                    "Priority": document_priority(row.get("Risk", ""), row.get("Status", "")),
                    "Source area": "DMF",
                    "Source item": str(row.get("DMF section", "")),
                    "Key point": str(row.get("Expected information", "")),
                    "Why it matters": str(row.get("DP linkage", "")),
                    "Evidence required": str(row.get("Document source", "")),
                    "Affected CTD": "3.2.S / 3.2.P bridge",
                    "Suggested action": str(row.get("Action", "")),
                    "User decision": "Open",
                }
            )

    ctd_documents = st.session_state.get("ctd_document_df", pd.DataFrame()).copy()
    if not ctd_documents.empty:
        focus = ctd_documents[
            ctd_documents.get("Risk", pd.Series(dtype=str)).isin(["High", "Medium"])
            | ctd_documents.get("Status", pd.Series(dtype=str)).isin(["Gap", "Partial"])
        ]
        for _, row in focus.iterrows():
            rows.append(
                {
                    "Priority": document_priority(row.get("Risk", ""), row.get("Status", "")),
                    "Source area": str(row.get("CTD module", "")),
                    "Source item": str(row.get("CTD part", "")),
                    "Key point": str(row.get("Expected information", "")),
                    "Why it matters": str(row.get("Evidence use", "")),
                    "Evidence required": str(row.get("Document source", "")),
                    "Affected CTD": str(row.get("CTD part", "")),
                    "Suggested action": str(row.get("Next action", "")),
                    "User decision": "Open",
                }
            )

    points = pd.DataFrame(rows)
    if points.empty:
        return points
    priority_order = {"Critical": 0, "Watch": 1, "Info": 2}
    points["_priority_order"] = points["Priority"].map(priority_order).fillna(9)
    points = points.sort_values(["_priority_order", "Source area", "Source item"]).drop(columns=["_priority_order"])
    return points.reset_index(drop=True)


def merge_user_decision_edits(generated: pd.DataFrame) -> pd.DataFrame:
    previous = st.session_state.get("document_decision_df")
    if not isinstance(previous, pd.DataFrame) or previous.empty or generated.empty:
        return generated
    key_columns = ["Source area", "Source item"]
    if not all(column in previous.columns and column in generated.columns for column in key_columns):
        return generated
    editable_columns = [
        "Priority",
        "Why it matters",
        "Evidence required",
        "Affected CTD",
        "Suggested action",
        "User decision",
    ]
    merged = generated.copy()
    previous = previous.drop_duplicates(key_columns, keep="last").set_index(key_columns)
    for idx, row in merged.iterrows():
        key = tuple(row[column] for column in key_columns)
        if key not in previous.index:
            continue
        old_row = previous.loc[key]
        for column in editable_columns:
            if column in merged.columns and column in previous.columns:
                old_value = old_row[column]
                if str(old_value).strip():
                    merged.at[idx, column] = old_value
    return merged


def dmf_element_from_source(section: Any) -> str:
    text = str(section).lower()
    if "loa" in text or "authorization" in text or "administrative" in text:
        return "Letter of authorization"
    if "identity" in text or "grade" in text or "s.1" in text:
        return "API identity / grade"
    if "manufacture" in text or "supplier" in text or "s.2" in text:
        return "API manufacturing / supplier control"
    if "impurity" in text or "characterisation" in text or "characterization" in text or "s.3" in text:
        return "Impurity profile"
    if "specification" in text or "method" in text or "s.4" in text:
        return "API specification / methods"
    if "stability" in text or "retest" in text or "s.7" in text:
        return "Retest period / storage"
    return str(section)


def verification_from_status(status: Any) -> str:
    status_text = str(status)
    if status_text == "Ready":
        return "Verified"
    if status_text == "Gap":
        return "Gap"
    if status_text == "N/A":
        return "N/A"
    return "Partial"


def update_or_append_row(df: pd.DataFrame, match_column: str, match_value: str, row_values: dict[str, Any]) -> tuple[pd.DataFrame, bool]:
    updated = df.copy()
    if match_column not in updated.columns:
        updated[match_column] = ""
    mask = updated[match_column].astype(str).eq(str(match_value))
    if mask.any():
        first_index = updated.index[mask][0]
        for column, value in row_values.items():
            if column not in updated.columns:
                updated[column] = ""
            updated.at[first_index, column] = value
        return updated, True
    for column in row_values:
        if column not in updated.columns:
            updated[column] = ""
    updated = pd.concat([updated, pd.DataFrame([row_values])], ignore_index=True)
    return updated, False


def apply_document_inputs_to_workbench(profile: dict[str, Any] | None = None) -> dict[str, int]:
    ctd_documents = st.session_state.get("ctd_document_df", pd.DataFrame()).copy()
    dmf_source = st.session_state.get("dmf_source_df", pd.DataFrame()).copy()
    evidence_updates = 0
    dmf_updates = 0
    spec_updates = 0

    evidence = st.session_state.get("evidence_df", pd.DataFrame(default_evidence_rows())).copy()
    if not ctd_documents.empty:
        for _, row in ctd_documents[ctd_documents["CTD module"].isin(["3.2.S", "3.2.P"])].iterrows():
            section = str(row.get("CTD part", "")).strip()
            if not section:
                continue
            source_text = str(row.get("Document text / excerpt", "")).strip()
            confirmed = str(row.get("Confirmed value", "")).strip()
            source_document = str(row.get("Document source", "")).strip()
            source_note = source_document
            if confirmed:
                source_note = f"{source_note} | Confirmed: {confirmed}" if source_note else f"Confirmed: {confirmed}"
            if source_text:
                source_note = f"{source_note} | Source text entered" if source_note else "Source text entered"
            evidence, _ = update_or_append_row(
                evidence,
                "CTD section",
                section,
                {
                    "CTD module": str(row.get("CTD module", "")),
                    "CTD section": section,
                    "Core question": str(row.get("Expected information", "")),
                    "Status": str(row.get("Status", "")),
                    "Source document": source_note,
                    "Owner": str(row.get("Owner", "")),
                    "Risk": str(row.get("Risk", "")),
                    "Next action": str(row.get("Next action", "")),
                },
            )
            evidence_updates += 1
    st.session_state.evidence_df = evidence

    dmf = st.session_state.get("dmf_df", pd.DataFrame(default_dmf_rows())).copy()
    if not dmf_source.empty:
        for _, row in dmf_source.iterrows():
            element = dmf_element_from_source(row.get("DMF section", ""))
            source = str(row.get("Document source", "")).strip()
            confirmed = str(row.get("Confirmed value", "")).strip()
            evidence_text = source
            if confirmed:
                evidence_text = f"{evidence_text} | Confirmed: {confirmed}" if evidence_text else f"Confirmed: {confirmed}"
            dmf, _ = update_or_append_row(
                dmf,
                "DMF element",
                element,
                {
                    "DMF element": element,
                    "API / supplier evidence": evidence_text or str(row.get("Expected information", "")),
                    "DP impact": str(row.get("DP linkage", "")),
                    "Applicant verification": verification_from_status(row.get("Status", "")),
                    "Risk": str(row.get("Risk", "")),
                    "Action": str(row.get("Action", "")),
                },
            )
            dmf_updates += 1
    st.session_state.dmf_df = dmf

    spec = st.session_state.get("spec_df", pd.DataFrame(default_spec_rows())).copy()
    p5_focus = ctd_documents[
        ctd_documents.get("CTD part", pd.Series(dtype=str)).astype(str).str.contains("3.2.P.5", na=False)
        & ctd_documents.get("Status", pd.Series(dtype=str)).isin(["Partial", "Gap"])
    ]
    if not p5_focus.empty:
        p5_row = p5_focus.iloc[0]
        spec, _ = update_or_append_row(
            spec,
            "Test item",
            "Document-derived P.5 control strategy gap",
            {
                "Test item": "Document-derived P.5 control strategy gap",
                "Acceptance criterion": "Define from DP specification, batch data, stability, method validation, and safety/performance relevance",
                "Method": str(p5_row.get("Document source", "")),
                "Validation status": "Partial" if str(p5_row.get("Status", "")) == "Partial" else "Not validated",
                "Rationale basis": str(p5_row.get("Confirmed value", "")) or str(p5_row.get("Expected information", "")),
                "Linked CQA": str(p5_row.get("Evidence use", "")),
                "Risk": str(p5_row.get("Risk", "")),
                "Reviewer question": "Can each P.5 acceptance criterion be defended in P.5.6 with source data and validated method capability?",
            },
        )
        spec_updates = 1
    st.session_state.spec_df = spec

    st.session_state.document_decision_df = merge_user_decision_edits(document_decision_points(profile or current_profile_from_state()))
    return {
        "evidence_updates": evidence_updates,
        "dmf_updates": dmf_updates,
        "spec_updates": spec_updates,
    }


def current_profile_from_state() -> dict[str, Any]:
    return {
        "product": str(st.session_state.get("product", "Naltrexone PLGA depot injection")),
        "active_substance": str(st.session_state.get("active_substance", "Naltrexone")),
        "api_supplier": str(st.session_state.get("api_supplier", "API supplier / DMF holder to confirm")),
        "dosage": str(st.session_state.get("dosage", "PLGA microsphere extended-release injection")),
        "formulation_platform": str(st.session_state.get("formulation_platform", "PLGA long-acting microsphere")),
        "strength": str(st.session_state.get("strength", "380 mg/vial")),
        "route": str(st.session_state.get("route", "Intramuscular")),
        "clinical_material": str(st.session_state.get("clinical_material", "Clinical batch genealogy to confirm")),
        "reference": str(st.session_state.get("reference", "Vivitrol 380 mg or target reference")),
        "target_regions": str(st.session_state.get("target_regions", "US / Korea / EU strategy to confirm")),
        "stage": str(st.session_state.get("stage", "Submission prep")),
    }


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


def query_value(name: str, default: str = "") -> str:
    value = st.query_params.get(name, default)
    if isinstance(value, list):
        return str(value[0]) if value else default
    return str(value)


def requested_language_key() -> str:
    value = query_value("lang", str(st.session_state.get("lang", "en"))).lower()
    if value in {"ko", "kor", "korean", "한국어"}:
        return "ko"
    return "en"


def page_href(page_key: str, lang: str) -> str:
    safe_page = page_key if page_key in {str(item["key"]) for item in NAV_ITEMS} else "intake"
    safe_lang = "en" if lang == "en" else "ko"
    return f"?enter=1&page={safe_page}&lang={safe_lang}"


def current_page_key() -> str:
    allowed = {str(item["key"]) for item in NAV_ITEMS}
    page = query_value("page", "intake").lower()
    return page if page in allowed else "intake"


def should_show_landing() -> bool:
    if st.session_state.get("entered_app"):
        return False
    if entered_from_query():
        st.session_state.entered_app = True
        return False
    return True


def render_landing() -> None:
    lang = requested_language_key()
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
          <a class="tg-landing-link" href="?enter=1&lang={lang}" target="_self" aria-label="Enter ToxiGuard-VCC workbench">
            {image_markup}
            <span class="tg-enter-panel">
              <span class="tg-enter-button">{escape(tr(lang, "enter_workbench"))}</span>
              <span class="tg-enter-note">{escape(tr(lang, "landing_enter_note"))}</span>
            </span>
          </a>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button(tr(lang, "enter_workbench"), key="landing_enter_button", type="primary"):
        st.session_state.entered_app = True
        st.query_params["enter"] = "1"
        st.query_params["lang"] = lang
        st.rerun()


def render_header(lang: str) -> None:
    image_src = platform_image_data_uri()
    background = (
        f'background-image: linear-gradient(90deg, rgba(7, 27, 61, 0.88), rgba(7, 27, 61, 0.55)), url("{image_src}");'
        if image_src
        else "background: #071b3d;"
    )
    hero_pills = "".join(
        f'<span class="tg-tone-{escape(str(module["tone"]))}">'
        f'{svg_icon(str(module["icon"]))}'
        f'{escape(str(module.get("title_ko" if lang == "ko" else "title", module["title"])).replace(" Review", ""))}'
        f'</span>'
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
            grid-template-columns: repeat(auto-fit, minmax(116px, 1fr));
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
            grid-template-columns: repeat(auto-fit, minmax(188px, 1fr));
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
          .tg-validation-grid {{
            display: grid;
            grid-template-columns: repeat(5, minmax(0, 1fr));
            gap: 10px;
            margin: 10px 0 8px;
          }}
          .tg-validation-card {{
            min-height: 166px;
            border: 1px solid #d9e3ef;
            border-top: 4px solid var(--tg-accent, #087f86);
            border-radius: 8px;
            padding: 13px 12px;
            background: #ffffff;
            box-shadow: 0 10px 24px rgba(7, 27, 61, 0.06);
          }}
          .tg-validation-card.is-selected {{
            background: linear-gradient(180deg, var(--tg-accent-soft, #e2f4f2), #ffffff 74%);
            border-color: color-mix(in srgb, var(--tg-accent, #087f86) 58%, white);
            box-shadow: 0 18px 34px rgba(7, 27, 61, 0.12);
          }}
          .tg-validation-icon {{
            display: inline-grid;
            place-items: center;
            width: 44px;
            height: 44px;
            border-radius: 8px;
            color: var(--tg-accent-strong, #006068);
            background: var(--tg-accent-soft, #e2f4f2);
            border: 1px solid color-mix(in srgb, var(--tg-accent, #087f86) 30%, white);
          }}
          .tg-validation-card.is-selected .tg-validation-icon {{
            color: #ffffff;
            background: var(--tg-accent, #087f86);
            border-color: var(--tg-accent, #087f86);
          }}
          .tg-validation-title {{
            margin: 10px 0 4px;
            color: #071b3d;
            font-size: 0.92rem;
            font-weight: 900;
            line-height: 1.25;
          }}
          .tg-validation-copy {{
            margin: 0;
            color: #5d6a7f;
            font-size: 0.72rem;
            font-weight: 700;
            line-height: 1.35;
          }}
          .tg-validation-state {{
            display: inline-flex;
            align-items: center;
            min-height: 22px;
            margin-top: 8px;
            border-radius: 999px;
            padding: 3px 8px;
            color: var(--tg-accent-strong, #006068);
            background: var(--tg-accent-soft, #e2f4f2);
            font-size: 0.66rem;
            font-weight: 900;
            text-transform: uppercase;
          }}
          .tg-basis-panel {{
            margin: 12px 0 14px;
            padding: 15px 16px;
            border: 1px solid #d9e3ef;
            border-left: 5px solid var(--tg-accent, #c45b1d);
            border-radius: 8px;
            background: linear-gradient(90deg, var(--tg-accent-soft, #fde7dc), #ffffff 62%);
            color: #071b3d;
          }}
          .tg-basis-panel h3 {{
            margin: 0 0 7px;
            font-size: 1rem;
            line-height: 1.25;
          }}
          .tg-basis-panel p {{
            margin: 4px 0;
            color: #4c5b70;
            line-height: 1.45;
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
            .tg-validation-grid {{
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
            .tg-validation-grid {{
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
    product = st.sidebar.text_input(tr(lang, "product"), value="Naltrexone PLGA depot injection")
    active_substance = st.sidebar.text_input(tr(lang, "active_substance"), value="Naltrexone")
    api_supplier = st.sidebar.text_input(tr(lang, "api_supplier"), value="API supplier / DMF holder to confirm")
    dosage = st.sidebar.text_input(tr(lang, "dosage_form"), value="PLGA microsphere extended-release injection")
    formulation_platform = st.sidebar.text_input(tr(lang, "formulation_platform"), value="PLGA long-acting microsphere")
    strength = st.sidebar.text_input(tr(lang, "strength"), value="380 mg/vial")
    route = st.sidebar.text_input(tr(lang, "route"), value="Intramuscular")
    clinical_material = st.sidebar.text_input(tr(lang, "clinical_material"), value="Clinical batch genealogy to confirm")
    reference = st.sidebar.text_input(tr(lang, "reference"), value="Vivitrol 380 mg or target reference")
    target_regions = st.sidebar.text_input(tr(lang, "target_regions"), value="US / Korea / EU strategy to confirm")
    stage_options = ["Development", "Validation", "Submission prep", "Response", "Lifecycle change"]
    stage_display = option_labels(stage_options, lang)
    stage_label = st.sidebar.selectbox(tr(lang, "lifecycle_stage"), stage_display, index=2)
    stage = str(delocalize_value(stage_label, lang))
    st.sidebar.divider()
    st.sidebar.caption(tr(lang, "github_target"))
    st.sidebar.code("lyn0109-Toxi/ToxiGuard-VCC", language=None)
    st.sidebar.caption(f"Build: {APP_BUILD}")
    return {
        "product": product,
        "active_substance": active_substance,
        "api_supplier": api_supplier,
        "dosage": dosage,
        "formulation_platform": formulation_platform,
        "strength": strength,
        "route": route,
        "clinical_material": clinical_material,
        "reference": reference,
        "target_regions": target_regions,
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


def edit_status_risk_table(df: pd.DataFrame, lang: str, key: str, status_options: list[str] | None = None) -> pd.DataFrame:
    status_options = status_options or STATUS_OPTIONS
    status_col = tr(lang, "status")
    risk_col = tr(lang, "risk")
    return delocalize_dataframe(
        st.data_editor(
            localize_dataframe(df, lang),
            width="stretch",
            num_rows="dynamic",
            column_config={
                status_col: st.column_config.SelectboxColumn(status_col, options=option_labels(status_options, lang), required=True),
                risk_col: st.column_config.SelectboxColumn(risk_col, options=option_labels(RISK_OPTIONS, lang), required=True),
            },
            key=key,
        ),
        lang,
    )


def update_subset_frame(state_key: str, edited_subset: pd.DataFrame, filter_column: str, filter_value: str) -> None:
    current = st.session_state[state_key].copy()
    remaining = current[current[filter_column] != filter_value]
    st.session_state[state_key] = pd.concat([remaining, edited_subset], ignore_index=True)


def render_icon_nav(lang: str, current_page: str) -> None:
    items = []
    for item in NAV_ITEMS:
        key = str(item["key"])
        label = tr(lang, str(item["label_key"]))
        description = str(item.get("description_ko" if lang == "ko" else "description", item["description"]))
        is_active = key == current_page
        active_attr = ' aria-current="page"' if is_active else ""
        state_markup = f'<span class="tg-nav-state">{escape(tr(lang, "selected"))}</span>' if is_active else '<span class="tg-nav-state" aria-hidden="true"></span>'
        items.append(
            f'<a class="tg-nav-item tg-tone-{escape(str(item["tone"]))}" href="{escape(page_href(key, lang))}" '
            f'target="_self" aria-label="{escape(label)}"{active_attr}>'
            f'<span class="tg-nav-icon">{svg_icon(str(item["icon"]))}</span>'
            f'<span class="tg-nav-copy">'
            f'<span class="tg-nav-label">{escape(label)}</span>'
            f'<span class="tg-nav-desc">{escape(description)}</span>'
            f'</span>'
            f'{state_markup}'
            f'</a>'
        )
    st.markdown(f'<nav class="tg-icon-nav" aria-label="ToxiGuard module menu">{"".join(items)}</nav>', unsafe_allow_html=True)


def build_meeting_summary(profile: dict[str, Any]) -> str:
    lang = str(st.session_state.get("lang", "ko"))
    intake = st.session_state.intake_df
    readiness = score_intake(intake)
    question_count = intake_gap_count(intake)
    high_count = int((intake["Risk"] == "High").sum()) if not intake.empty else 0
    focus = intake_focus_rows(intake)
    top_area = str(focus.iloc[0]["Intake area"]) if not focus.empty else "Current intake"
    top_question = str(focus.iloc[0]["Client question"]) if not focus.empty else "No major client question is currently triggered."
    top_update = str(focus.iloc[0]["CTD update direction"]) if not focus.empty else "N/A"
    if lang == "ko":
        return (
            f"제품: {profile['product']}\n"
            "미팅 목적: 고객이 제공한 문서를 gap/risk 요약, 고객 질문, CTD 업데이트 방향으로 전환합니다.\n"
            f"문서 접수 준비도: {readiness}%\n"
            f"미해결 고객 질문: {question_count}\n"
            f"고위험 접수 항목: {high_count}\n"
            f"첫 논의 초점: {top_area}\n"
            f"우선 고객 질문: {top_question}\n"
            f"예상 CTD 업데이트 방향: {top_update}"
        )
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
    lang = str(st.session_state.get("lang", "ko"))
    steps = [
        ("1", tr(lang, "document_received"), "DMF / DP / method package"),
        ("2", tr(lang, "input"), "status, quality, risk" if lang == "en" else "상태, 품질, 리스크"),
        ("3", tr(lang, "gap_risk_summary"), tr(lang, "meeting_ready_view")),
        ("4", tr(lang, "client_questions"), tr(lang, "evidence_request_list")),
        ("5", tr(lang, "ctd_direction"), tr(lang, "update_target_section")),
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

    st.session_state.intake_df = delocalize_dataframe(
        st.data_editor(
            localize_dataframe(st.session_state.intake_df, lang),
            width="stretch",
            num_rows="dynamic",
            column_config={
                tr(lang, "received"): st.column_config.SelectboxColumn(
                    tr(lang, "received"), options=option_labels(INTAKE_RECEIVED_OPTIONS, lang), required=True
                ),
                tr(lang, "quality"): st.column_config.SelectboxColumn(
                    tr(lang, "quality"), options=option_labels(INTAKE_QUALITY_OPTIONS, lang), required=True
                ),
                tr(lang, "risk"): st.column_config.SelectboxColumn(
                    tr(lang, "risk"), options=option_labels(RISK_OPTIONS, lang), required=True
                ),
            },
            key="intake_editor",
        ),
        lang,
    )

    intake = st.session_state.intake_df
    readiness = score_intake(intake)
    question_count = intake_gap_count(intake)
    high_count = int((intake["Risk"] == "High").sum()) if not intake.empty else 0
    missing_count = int((intake["Received"] == "Missing").sum()) if not intake.empty else 0

    k1, k2, k3, k4 = st.columns(4)
    k1.metric(tr(lang, "intake_readiness"), f"{readiness}%")
    k2.metric(tr(lang, "client_questions"), question_count)
    k3.metric(tr(lang, "open_risk"), high_count)
    k4.metric("Missing documents" if lang == "en" else "누락 문서", missing_count)

    summary = build_meeting_summary(profile)
    mini_heading(tr(lang, "meeting_summary"), "clipboard_check", "teal")
    st.markdown(
        f'<div class="tg-summary-box tg-tone-teal">{escape(summary).replace(chr(10), "<br>")}</div>',
        unsafe_allow_html=True,
    )

    focus = intake_focus_rows(intake)
    mini_heading(tr(lang, "client_questions"), "alert", "orange")
    st.dataframe(
        display_dataframe(focus, lang, ["Intake area", "Client question", "Expected client document", "Risk"]),
        width="stretch",
        hide_index=True,
    )

    mini_heading(tr(lang, "ctd_update_direction"), "file_pen", "blue")
    st.dataframe(
        display_dataframe(focus, lang, ["Intake area", "CTD update direction", "Risk"]),
        width="stretch",
        hide_index=True,
    )


def render_document_workspace(lang: str, profile: dict[str, Any]) -> None:
    section_header(tr(lang, "document_workspace"), tr(lang, "document_workspace_help"), "file_pen", "blue")

    ctd_ready = score_document_inputs(st.session_state.ctd_document_df)
    dmf_ready = score_document_inputs(st.session_state.dmf_source_df)
    text_entries = source_text_count(st.session_state.ctd_document_df, st.session_state.dmf_source_df)
    open_doc_risks = count_high_risks(st.session_state.ctd_document_df, st.session_state.dmf_source_df)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric(tr(lang, "ctd_document_readiness"), f"{ctd_ready}%")
    k2.metric(tr(lang, "dmf_document_readiness"), f"{dmf_ready}%")
    k3.metric(tr(lang, "source_text_entries"), text_entries)
    k4.metric(tr(lang, "open_risk"), open_doc_risks)

    mini_heading(tr(lang, "document_logic"), "network", "teal")
    st.caption(tr(lang, "document_logic_help"))
    st.info(tr(lang, "document_review_boundary"))
    st.session_state.document_logic_df = edit_status_risk_table(
        st.session_state.document_logic_df,
        lang,
        "document_logic_editor",
        STATUS_OPTIONS,
    )

    mini_heading(tr(lang, "key_decision_points"), "alert", "orange")
    decision_points = merge_user_decision_edits(document_decision_points(profile))
    priority_col = COLUMN_KO.get("Priority", "Priority") if lang == "ko" else "Priority"
    user_decision_col = COLUMN_KO.get("User decision", "User decision") if lang == "ko" else "User decision"
    st.session_state.document_decision_df = delocalize_dataframe(
        st.data_editor(
            localize_dataframe(decision_points, lang),
            width="stretch",
            num_rows="dynamic",
            column_config={
                priority_col: st.column_config.SelectboxColumn(
                    priority_col,
                    options=option_labels(["Critical", "Watch", "Info"], lang),
                    required=True,
                ),
                user_decision_col: st.column_config.SelectboxColumn(
                    user_decision_col,
                    options=option_labels(["Open", "Accept", "Revise", "Escalate"], lang),
                    required=True,
                ),
            },
            key="document_decision_editor",
        ),
        lang,
    )
    apply_col, help_col = st.columns([1.2, 3])
    with apply_col:
        if st.button(tr(lang, "apply_document_inputs"), type="primary", use_container_width=True):
            result = apply_document_inputs_to_workbench(profile)
            st.success(
                f"{tr(lang, 'apply_document_inputs_done')} "
                f"Evidence Map {result['evidence_updates']} / DMF Bridge {result['dmf_updates']} / P.5.6 seed {result['spec_updates']}"
            )
    with help_col:
        st.caption(tr(lang, "apply_document_inputs_help"))

    mini_heading(tr(lang, "profile_driven_prompts"), "gauge", "blue")
    st.dataframe(
        display_dataframe(product_profile_prompts(profile), lang),
        width="stretch",
        hide_index=True,
    )

    st.info(tr(lang, "document_input_strategy"))
    tabs = st.tabs(
        [
            tr(lang, "dmf_source_input"),
            tr(lang, "ctd_3_2_s_input"),
            tr(lang, "ctd_3_2_p_input"),
            tr(lang, "ctd_other_parts_input"),
        ]
    )

    with tabs[0]:
        mini_heading(tr(lang, "dmf_source_input"), "bridge", "blue")
        st.session_state.dmf_source_df = edit_status_risk_table(
            st.session_state.dmf_source_df,
            lang,
            "dmf_source_editor",
            STATUS_OPTIONS,
        )
        high_dmf_source = st.session_state.dmf_source_df[st.session_state.dmf_source_df["Risk"] == "High"]
        if not high_dmf_source.empty:
            st.warning(
                "High-risk DMF source inputs must be clarified before the DMF-to-DP bridge is defensible."
                if lang == "en"
                else "DMF 원문 입력의 고위험 항목은 DMF-to-DP bridge를 방어하기 전에 먼저 확인해야 합니다."
            )
            st.dataframe(
                display_dataframe(high_dmf_source, lang, ["DMF section", "Expected information", "DP linkage", "Action"]),
                width="stretch",
                hide_index=True,
            )
        notes = st.session_state.setdefault("document_notes", {"dmf": "", "ctd_s": "", "ctd_p": "", "ctd_other": ""})
        notes["dmf"] = st.text_area(
            tr(lang, "raw_document_paste"),
            value=str(notes.get("dmf", "")),
            height=180,
            key="dmf_long_source_note",
            placeholder="Paste DMF/LoA/COA excerpt here..." if lang == "en" else "DMF, LoA, COA 발췌문을 여기에 입력하세요...",
        )
        st.session_state.document_notes = notes

    for tab, module, key, title_key in [
        (tabs[1], "3.2.S", "ctd_s_editor", "ctd_3_2_s_input"),
        (tabs[2], "3.2.P", "ctd_p_editor", "ctd_3_2_p_input"),
        (tabs[3], "Other CTD", "ctd_other_editor", "ctd_other_parts_input"),
    ]:
        with tab:
            mini_heading(tr(lang, title_key), "file_pen", "teal" if module == "3.2.P" else "blue")
            subset = st.session_state.ctd_document_df[st.session_state.ctd_document_df["CTD module"] == module].copy()
            edited = edit_status_risk_table(subset, lang, key, STATUS_OPTIONS)
            update_subset_frame("ctd_document_df", edited, "CTD module", module)
            high_subset = edited[edited["Risk"] == "High"]
            if not high_subset.empty:
                st.warning(
                    "High-risk CTD source inputs should be linked to source text, confirmed values, and next actions."
                    if lang == "en"
                    else "고위험 CTD 입력 항목은 원문 발췌, 확인값, 다음 조치와 연결되어야 합니다."
                )
                st.dataframe(
                    display_dataframe(high_subset, lang, ["CTD part", "Expected information", "Evidence use", "Next action"]),
                    width="stretch",
                    hide_index=True,
                )
            notes = st.session_state.setdefault("document_notes", {"dmf": "", "ctd_s": "", "ctd_p": "", "ctd_other": ""})
            note_key = {"3.2.S": "ctd_s", "3.2.P": "ctd_p"}.get(module, "ctd_other")
            notes[note_key] = st.text_area(
                tr(lang, "raw_document_paste"),
                value=str(notes.get(note_key, "")),
                height=180,
                key=f"{key}_long_source_note",
                placeholder=(
                    f"Paste {module} CTD source excerpt here..."
                    if lang == "en"
                    else f"{module} CTD 원문 발췌문을 여기에 입력하세요..."
                ),
            )
            st.session_state.document_notes = notes


def render_selected_page(page_key: str, lang: str, profile: dict[str, Any]) -> None:
    if page_key == "intake":
        render_client_intake(lang, profile)
    elif page_key == "documents":
        render_document_workspace(lang, profile)
    elif page_key == "evidence":
        render_evidence_map(lang, profile)
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
    ctd_document_readiness = score_document_inputs(st.session_state.ctd_document_df)
    dmf_document_readiness = score_document_inputs(st.session_state.dmf_source_df)
    combined_readiness = round((intake_readiness + readiness + ctd_document_readiness + dmf_document_readiness) / 4, 1)
    source_entries = source_text_count(st.session_state.ctd_document_df, st.session_state.dmf_source_df)
    high_risks = count_high_risks(
        st.session_state.intake_df,
        st.session_state.evidence_df,
        st.session_state.spec_df,
        st.session_state.dmf_df,
        st.session_state.ctd_document_df,
        st.session_state.dmf_source_df,
    )
    gate, gate_message = decision_gate(combined_readiness, high_risks)
    gate_display = str(localize_value(gate, lang))
    gate_note = gate_message
    if lang == "ko":
        gate_note = {
            "Evidence package is close to review-ready.": "근거 패키지가 검토 준비 상태에 가깝습니다.",
            "Proceed with targeted gap closure before external use.": "외부 사용 전 주요 gap을 먼저 보완하세요.",
            "Resolve high-risk evidence gaps before relying on the package.": "패키지에 의존하기 전 고위험 근거 gap을 해결해야 합니다.",
        }.get(gate_message, gate_message)
    kpi_markup = f"""
    <div class="tg-kpi-grid">
      <div class="tg-kpi-card tg-tone-teal">
        <div class="tg-kpi-head">
          <span class="tg-kpi-icon">{svg_icon("clipboard_check")}</span>
          <div class="tg-kpi-label">{escape(tr(lang, "intake_readiness"))}</div>
        </div>
        <div class="tg-kpi-value">{intake_readiness}%</div>
        <div class="tg-kpi-note">{escape(tr(lang, "client_document_usability"))}</div>
      </div>
      <div class="tg-kpi-card tg-tone-teal">
        <div class="tg-kpi-head">
          <span class="tg-kpi-icon">{svg_icon("gauge")}</span>
          <div class="tg-kpi-label">{escape(tr(lang, "readiness"))}</div>
        </div>
        <div class="tg-kpi-value">{readiness}%</div>
        <div class="tg-kpi-note">{escape(tr(lang, "source_readiness"))}</div>
      </div>
      <div class="tg-kpi-card tg-tone-blue">
        <div class="tg-kpi-head">
          <span class="tg-kpi-icon">{svg_icon("file_pen")}</span>
          <div class="tg-kpi-label">{escape(tr(lang, "ctd_document_readiness"))}</div>
        </div>
        <div class="tg-kpi-value">{ctd_document_readiness}%</div>
        <div class="tg-kpi-note">3.2.S / 3.2.P / Other CTD</div>
      </div>
      <div class="tg-kpi-card tg-tone-amber">
        <div class="tg-kpi-head">
          <span class="tg-kpi-icon">{svg_icon("bridge")}</span>
          <div class="tg-kpi-label">{escape(tr(lang, "dmf_document_readiness"))}</div>
        </div>
        <div class="tg-kpi-value">{dmf_document_readiness}%</div>
        <div class="tg-kpi-note">DMF source input</div>
      </div>
      <div class="tg-kpi-card tg-tone-orange">
        <div class="tg-kpi-head">
          <span class="tg-kpi-icon">{svg_icon("alert")}</span>
          <div class="tg-kpi-label">{escape(tr(lang, "source_text_entries"))}</div>
        </div>
        <div class="tg-kpi-value">{source_entries}</div>
        <div class="tg-kpi-note">{escape(tr(lang, "questions_to_ask"))}: {intake_gap_count(st.session_state.intake_df)}</div>
      </div>
      <div class="tg-kpi-card tg-tone-blue">
        <div class="tg-kpi-head">
          <span class="tg-kpi-icon">{svg_icon("shield")}</span>
          <div class="tg-kpi-label">{escape(tr(lang, "decision"))}</div>
        </div>
        <div class="tg-kpi-value">{escape(gate_display)}</div>
        <div class="tg-kpi-note">{escape(gate_note)}</div>
      </div>
    </div>
    """
    st.markdown(kpi_markup, unsafe_allow_html=True)

    cards = []
    for module in MODULES:
        title = module.get("title_ko" if lang == "ko" else "title", module["title"])
        output = module.get("output_ko" if lang == "ko" else "output", module["output"])
        risk = module.get("risk_ko" if lang == "ko" else "risk", module["risk"])
        cards.append(
            f'<article class="tg-module-card tg-tone-{escape(str(module["tone"]))}">'
            f'<div class="tg-module-top">'
            f'<div class="tg-module-identity">'
            f'<span class="tg-module-icon">{svg_icon(str(module["icon"]))}</span>'
            f'<span class="tg-step">{escape(module["no"])}</span>'
            f'</div>'
            f'<span class="tg-status-pill">{escape(tr(lang, "live"))}</span>'
            f'</div>'
            f'<h3>{escape(str(title))}</h3>'
            f'<p>{escape(str(output))}</p>'
            f'<div class="tg-risk"><strong>{escape(tr(lang, "risk_watch"))}</strong><br>{escape(str(risk))}</div>'
            f'</article>'
        )
    st.markdown(
        f'<div class="tg-section-title">{escape(tr(lang, "core_modules"))}</div>'
        f'<div style="color:#4c5b70; margin-bottom: 14px;">{escape(tr(lang, "module_help"))}</div>'
        f'<div class="tg-module-grid">{"".join(cards)}</div>',
        unsafe_allow_html=True,
    )

    mini_heading(tr(lang, "decision_context"), "shield", "blue")
    st.dataframe(
        display_dataframe(
            pd.DataFrame(
            [
                [tr(lang, "product"), profile["product"]],
                [tr(lang, "dosage_form"), profile["dosage"]],
                [tr(lang, "strength"), profile["strength"]],
                [tr(lang, "route"), profile["route"]],
                [tr(lang, "reference"), profile["reference"]],
                [tr(lang, "lifecycle_stage"), localize_value(profile["stage"], lang)],
                [tr(lang, "active_substance"), profile["active_substance"]],
                [tr(lang, "api_supplier"), profile["api_supplier"]],
                [tr(lang, "formulation_platform"), profile["formulation_platform"]],
                [tr(lang, "clinical_material"), profile["clinical_material"]],
                [tr(lang, "target_regions"), profile["target_regions"]],
                [tr(lang, "intake_readiness"), f"{intake_readiness}%"],
                [tr(lang, "ctd_document_readiness"), f"{ctd_document_readiness}%"],
                [tr(lang, "dmf_document_readiness"), f"{dmf_document_readiness}%"],
                [tr(lang, "readiness"), f"{readiness}%"],
                [tr(lang, "client_questions"), str(intake_gap_count(st.session_state.intake_df))],
                [tr(lang, "open_risk"), str(high_risks)],
            ],
            columns=["Field", "Value"],
        ),
            lang,
        ),
        width="stretch",
        hide_index=True,
    )

    mini_heading(tr(lang, "key_decision_points"), "alert", "orange")
    st.dataframe(
        display_dataframe(
            document_decision_points(profile).head(12),
            lang,
            ["Priority", "Source area", "Source item", "Key point", "Why it matters", "Suggested action", "User decision"],
        ),
        width="stretch",
        hide_index=True,
    )


def render_evidence_map(lang: str, profile: dict[str, Any]) -> None:
    section_header(tr(lang, "evidence_map"), tr(lang, "evidence_map_help"), "network", "teal")
    tabs = st.tabs([tr(lang, "profile_driven_prompts"), "3.2.S", "3.2.P", "All CTD gaps" if lang == "en" else "전체 CTD gap"])
    with tabs[0]:
        mini_heading(tr(lang, "profile_driven_prompts"), "gauge", "blue")
        st.dataframe(display_dataframe(product_profile_prompts(profile), lang), width="stretch", hide_index=True)
    for tab, module, key in [(tabs[1], "3.2.S", "evidence_s_editor"), (tabs[2], "3.2.P", "evidence_p_editor")]:
        with tab:
            subset = st.session_state.evidence_df[st.session_state.evidence_df["CTD module"] == module].copy()
            edited = edit_status_risk_table(subset, lang, key, STATUS_OPTIONS)
            update_subset_frame("evidence_df", edited, "CTD module", module)
    with tabs[3]:
        st.dataframe(
            display_dataframe(
                st.session_state.evidence_df[
                    (st.session_state.evidence_df["Risk"].isin(["High", "Medium"]))
                    | (st.session_state.evidence_df["Status"].isin(["Partial", "Gap"]))
                ],
                lang,
                ["CTD module", "CTD section", "Status", "Risk", "Owner", "Next action"],
            ),
            width="stretch",
            hide_index=True,
        )

    high = st.session_state.evidence_df[st.session_state.evidence_df["Risk"] == "High"]
    if not high.empty:
        st.warning(
            "High-risk CTD sections need source-backed closure before the response memo is used."
            if lang == "en"
            else "RA 답변 메모를 사용하기 전에 고위험 CTD 항목은 근거 문서로 보완되어야 합니다."
        )
        st.dataframe(display_dataframe(high, lang, ["CTD module", "CTD section", "Status", "Owner", "Next action"]), width="stretch", hide_index=True)


def render_spec_rationale(lang: str) -> None:
    section_header(tr(lang, "spec_rationale"), tr(lang, "spec_help"), "target", "amber")
    st.session_state.spec_df = delocalize_dataframe(
        st.data_editor(
            localize_dataframe(st.session_state.spec_df, lang),
            width="stretch",
            num_rows="dynamic",
            column_config={
                COLUMN_KO.get("Validation status", "Validation status") if lang == "ko" else "Validation status": st.column_config.SelectboxColumn(
                    COLUMN_KO.get("Validation status", "Validation status") if lang == "ko" else "Validation status",
                    options=option_labels(VALIDATION_STATUS, lang),
                    required=True,
                ),
                tr(lang, "risk"): st.column_config.SelectboxColumn(
                    tr(lang, "risk"), options=option_labels(RISK_OPTIONS, lang), required=True
                ),
            },
            key="spec_editor",
        ),
        lang,
    )
    weak = st.session_state.spec_df[
        (st.session_state.spec_df["Risk"] == "High")
        | (st.session_state.spec_df["Validation status"].isin(["Partial", "Not validated"]))
    ]
    mini_heading("Reviewer-risk focus" if lang == "en" else "심사 리스크 집중 검토", "alert", "amber")
    st.dataframe(
        display_dataframe(weak, lang, ["Test item", "Acceptance criterion", "Validation status", "Risk", "Reviewer question"]),
        width="stretch",
        hide_index=True,
    )


def render_dmf_bridge(lang: str) -> None:
    section_header(tr(lang, "dmf_bridge"), tr(lang, "dmf_help"), "bridge", "blue")
    verification_options = ["Verified", "Partial", "Gap", "N/A"]
    st.session_state.dmf_df = delocalize_dataframe(
        st.data_editor(
            localize_dataframe(st.session_state.dmf_df, lang),
            width="stretch",
            num_rows="dynamic",
            column_config={
                COLUMN_KO.get("Applicant verification", "Applicant verification") if lang == "ko" else "Applicant verification": st.column_config.SelectboxColumn(
                    COLUMN_KO.get("Applicant verification", "Applicant verification") if lang == "ko" else "Applicant verification",
                    options=option_labels(verification_options, lang),
                    required=True,
                ),
                tr(lang, "risk"): st.column_config.SelectboxColumn(
                    tr(lang, "risk"), options=option_labels(RISK_OPTIONS, lang), required=True
                ),
            },
            key="dmf_editor",
        ),
        lang,
    )
    high = st.session_state.dmf_df[st.session_state.dmf_df["Risk"] == "High"]
    if not high.empty:
        st.error(
            "DMF-to-DP high-risk items should be closed before final CMC wording."
            if lang == "en"
            else "최종 CMC 문구를 작성하기 전에 DMF-완제 연결의 고위험 항목을 보완해야 합니다."
        )
        st.dataframe(display_dataframe(high, lang, ["DMF element", "DP impact", "Action"]), width="stretch", hide_index=True)


def concentration_review(profile: dict[str, Any]) -> dict[str, float | str | None]:
    lang = str(st.session_state.get("lang", "ko"))
    defaults = profile["prep_defaults"]
    prefix = f"prep_{profile['key']}"
    st.caption(profile_copy(profile, "sample_focus", lang))
    c1, c2, c3 = st.columns(3)
    with c1:
        reference_conc = st.number_input(
            "Reference concentration at 100%" if lang == "en" else "100% 기준농도",
            min_value=0.000001,
            value=float(defaults["reference_conc"]),
            step=0.1,
            format="%.6f",
            key=f"{prefix}_reference_conc",
        )
        unit = st.text_input("Concentration unit" if lang == "en" else "농도 단위", value=str(defaults["unit"]), key=f"{prefix}_unit")
        level_pct = st.number_input(
            "Validation level %" if lang == "en" else "밸리데이션 level %",
            min_value=0.0,
            value=float(defaults["level_pct"]),
            step=5.0,
            key=f"{prefix}_level_pct",
        )
    with c2:
        weighed_mg = st.number_input(
            "Actual weighed amount (mg)" if lang == "en" else "실제 칭량량 (mg)",
            min_value=0.0,
            value=float(defaults["weighed_mg"]),
            step=0.1,
            format="%.4f",
            key=f"{prefix}_weighed_mg",
        )
        purity_pct = st.number_input(
            "Purity / potency correction %" if lang == "en" else "순도 / 역가 보정 %",
            min_value=0.0,
            value=float(defaults["purity_pct"]),
            step=0.1,
            format="%.4f",
            key=f"{prefix}_purity_pct",
        )
        stock_volume_ml = st.number_input(
            "Stock final volume (mL)" if lang == "en" else "Stock 최종부피 (mL)",
            min_value=0.000001,
            value=float(defaults["stock_volume_ml"]),
            step=10.0,
            format="%.4f",
            key=f"{prefix}_stock_volume_ml",
        )
    with c3:
        aliquot_ml = st.number_input(
            "Aliquot taken from stock (mL)" if lang == "en" else "Stock에서 취한량 (mL)",
            min_value=0.0,
            value=float(defaults["aliquot_ml"]),
            step=0.1,
            format="%.4f",
            key=f"{prefix}_aliquot_ml",
        )
        final_volume_ml = st.number_input(
            "Final volume after aliquot (mL)" if lang == "en" else "희석 후 최종부피 (mL)",
            min_value=0.000001,
            value=float(defaults["final_volume_ml"]),
            step=10.0,
            format="%.4f",
            key=f"{prefix}_final_volume_ml",
        )
        dilution_factor = st.number_input(
            "Additional dilution factor" if lang == "en" else "추가 희석배수",
            min_value=0.000001,
            value=float(defaults["dilution_factor"]),
            step=0.5,
            format="%.4f",
            key=f"{prefix}_dilution_factor",
        )

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
    s1.metric("Stock concentration" if lang == "en" else "Stock 농도", f"{stock_conc:.4f} {unit}")
    s2.metric("Actual final concentration" if lang == "en" else "실제 최종농도", f"{final_conc:.4f} {unit}")
    s3.metric("Target concentration" if lang == "en" else "목표 농도", f"{target_conc:.4f} {unit}")
    s4.metric("Actual vs target" if lang == "en" else "목표 대비 차이", "N/A" if diff_pct is None else f"{float(diff_pct):+.2f}%")

    if calc["gate"] == "Pass":
        st.success(localize_note(str(calc["message"]), lang))
    elif calc["gate"] == "Review":
        st.warning(localize_note(str(calc["message"]), lang))
    else:
        st.error(localize_note(str(calc["message"]), lang))

    return {
        "test_item": validation_item_label(profile, "en"),
        "reference_conc": reference_conc,
        "unit": unit,
        "level_pct": level_pct,
        "stock_conc": stock_conc,
        "final_conc": final_conc,
        "target_conc": target_conc,
        "diff_pct": diff_pct,
        "gate": calc["gate"],
    }


def linearity_and_lod_review(reference_conc: float, unit: str, profile: dict[str, Any]) -> list[str]:
    lang = str(st.session_state.get("lang", "ko"))
    mini_heading("LOD / LOQ and intercept risk" if lang == "en" else "LOD / LOQ 및 intercept 리스크", "trend", "orange")
    defaults = profile["linearity_defaults"]
    prefix = f"linearity_{profile['key']}"
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        lod = st.number_input(
            "LOD",
            min_value=0.0,
            value=float(defaults["lod"]),
            step=0.01,
            format="%.6f",
            key=f"{prefix}_lod",
        )
        loq = st.number_input(
            "LOQ",
            min_value=0.0,
            value=float(defaults["loq"]),
            step=0.01,
            format="%.6f",
            key=f"{prefix}_loq",
        )
    with c2:
        r2 = st.number_input(
            "Linearity R2" if lang == "en" else "직선성 R2",
            min_value=0.0,
            max_value=1.0,
            value=float(defaults["r2"]),
            step=0.0001,
            format="%.6f",
            key=f"{prefix}_r2",
        )
        slope = st.number_input(
            "Mean slope" if lang == "en" else "평균 slope",
            value=float(defaults["slope"]),
            step=100.0,
            format="%.4f",
            key=f"{prefix}_slope",
        )
    with c3:
        intercept = st.number_input(
            "Mean intercept" if lang == "en" else "평균 intercept",
            value=float(defaults["intercept"]),
            step=10.0,
            format="%.4f",
            key=f"{prefix}_intercept",
        )
        response_100 = st.number_input(
            "Response at 100%" if lang == "en" else "100% response",
            min_value=0.000001,
            value=float(defaults["response_100"]),
            step=100.0,
            format="%.4f",
            key=f"{prefix}_response_100",
        )
    with c4:
        response_loq = st.number_input(
            "Response at LOQ" if lang == "en" else "LOQ response",
            min_value=0.000001,
            value=float(defaults["response_loq"]),
            step=50.0,
            format="%.4f",
            key=f"{prefix}_response_loq",
        )
        lowest_level_pct = st.number_input(
            "Lowest linearity level %" if lang == "en" else "최저 직선성 level %",
            min_value=0.0,
            value=float(defaults["lowest_level_pct"]),
            step=5.0,
            key=f"{prefix}_lowest_level_pct",
        )

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
    m1.metric("LOD / reference" if lang == "en" else "LOD / 기준농도", f"{lod_pct:.2f}%")
    m2.metric("LOQ / reference" if lang == "en" else "LOQ / 기준농도", f"{loq_pct:.2f}%")
    m3.metric("Intercept / 100% response" if lang == "en" else "Intercept / 100% response", f"{intercept_100_pct:.2f}%")
    m4.metric("Intercept / LOQ response" if lang == "en" else "Intercept / LOQ response", f"{intercept_loq_pct:.2f}%")

    notes = list(linearity["notes"])

    mini_heading(tr(st.session_state.lang, "risk_notes"), "alert", "orange")
    for note in notes:
        if "acceptable" in note:
            st.success(localize_note(note, lang))
        else:
            st.warning(localize_note(note, lang))

    return [
        f"{validation_item_label(profile, 'en')}: LOD {lod:.6f} {unit} ({lod_pct:.2f}% of reference)",
        f"{validation_item_label(profile, 'en')}: LOQ {loq:.6f} {unit} ({loq_pct:.2f}% of reference)",
        *notes,
    ]


def render_validation_test_selector(lang: str) -> dict[str, Any]:
    ensure_validation_item_tables()
    current = str(st.session_state.get("validation_test_item", "assay"))
    current = current if current in {str(profile["key"]) for profile in VALIDATION_TEST_ITEMS} else "assay"

    cards = []
    for profile in VALIDATION_TEST_ITEMS:
        key = str(profile["key"])
        df = st.session_state.validation_items[key].copy()
        df["Gate"] = df.apply(evaluate_rule, axis=1)
        review_count = int((df["Gate"] == "Review").sum())
        state = tr(lang, "selected") if key == current else str(localize_value("Review" if review_count else "Pass", lang))
        selected_class = " is-selected" if key == current else ""
        cards.append(
            f'<article class="tg-validation-card tg-tone-{escape(str(profile["tone"]))}{selected_class}">'
            f'<span class="tg-validation-icon">{svg_icon(str(profile["icon"]))}</span>'
            f'<div class="tg-validation-title">{escape(validation_item_label(profile, lang))}</div>'
            f'<p class="tg-validation-copy">{escape(profile_copy(profile, "purpose", lang))}</p>'
            f'<span class="tg-validation-state">{escape(state)} · {review_count} {"review" if lang == "en" else "검토"}</span>'
            f'</article>'
        )
    st.markdown(f'<div class="tg-validation-grid">{"".join(cards)}</div>', unsafe_allow_html=True)

    cols = st.columns(len(VALIDATION_TEST_ITEMS))
    for idx, profile in enumerate(VALIDATION_TEST_ITEMS):
        key = str(profile["key"])
        item_label = validation_item_label(profile, lang)
        label = f"{item_label} {tr(lang, 'selected')}" if key == current else (
            f"Open {item_label}" if lang == "en" else f"{item_label} {tr(lang, 'open_review')}"
        )
        with cols[idx]:
            if st.button(
                label,
                key=f"validation_select_{key}",
                use_container_width=True,
                type="primary" if key == current else "secondary",
            ):
                st.session_state.validation_test_item = key
                st.query_params["page"] = "validation"
                st.query_params["lang"] = lang
                st.rerun()

    return validation_profile(current)


def render_validation_basis_panel(profile: dict[str, Any], lang: str) -> None:
    title = validation_item_label(profile, lang)
    st.markdown(
        f"""
        <div class="tg-basis-panel tg-tone-{escape(str(profile["tone"]))}">
          <h3>{escape(title)} {escape(tr(lang, "validation_basis"))}</h3>
          <p><strong>{escape(tr(lang, "regulatory_basis"))}:</strong> {escape(str(profile["basis"]))}</p>
          <p><strong>{escape(tr(lang, "ctd_location"))}:</strong> {escape(str(profile["ctd"]))}</p>
          <p><strong>{escape(tr(lang, "m14_note"))}:</strong> {escape(profile_copy(profile, "m14", lang))}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_validation(lang: str) -> None:
    section_header(tr(lang, "validation"), tr(lang, "calc_help"), "calculator", "orange")
    mini_heading(tr(lang, "validation_select"), "shield", "orange")
    profile = render_validation_test_selector(lang)
    render_validation_basis_panel(profile, lang)

    mini_heading(tr(lang, "sample_prep"), "calculator", "orange")
    calc = concentration_review(profile)
    risk_notes = linearity_and_lod_review(float(calc["reference_conc"]), str(calc["unit"]), profile)

    mini_heading(tr(lang, "validation_gate"), "shield", "orange")
    tables = ensure_validation_item_tables()
    selected_key = str(profile["key"])
    required_inputs = "; ".join(str(item) for item in tables[selected_key]["Item"].head(8).tolist())
    st.info(f"{tr(lang, 'result_inputs')} - {validation_item_label(profile, lang)}: {required_inputs}")
    edited = st.data_editor(
        tables[selected_key],
        width="stretch",
        num_rows="dynamic",
        column_config={
            "Rule": st.column_config.SelectboxColumn("Rule", options=["between", "gte", "lte", "info"], required=True),
        },
        key=f"validation_editor_{selected_key}",
    )
    edited = edited.copy().drop(columns=["Gate"], errors="ignore")
    edited["Gate"] = edited.apply(evaluate_rule, axis=1)
    tables[selected_key] = edited.drop(columns=["Gate"], errors="ignore")
    st.session_state.validation_items = tables
    st.session_state.validation_df = tables["assay"].copy()

    st.dataframe(edited, width="stretch", hide_index=True)
    review_count = int((edited["Gate"] == "Review").sum())
    if review_count:
        st.warning(f"{review_count} {tr(lang, 'validation_review_warning')}")
    else:
        st.success(tr(lang, "validation_review_success"))

    mini_heading(tr(lang, "overall_validation_summary"), "trend", "orange")
    st.dataframe(display_dataframe(validation_summary_frame(), lang), width="stretch", hide_index=True)

    st.session_state["last_calc"] = calc
    st.session_state["last_risk_notes"] = risk_notes


def response_rows() -> pd.DataFrame:
    intake = st.session_state.intake_df
    evidence = st.session_state.evidence_df
    spec = st.session_state.spec_df
    dmf = st.session_state.dmf_df
    dmf_source = st.session_state.dmf_source_df
    ctd_documents = st.session_state.ctd_document_df
    validation = validation_review_frame(include_gate=True)
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
    for _, row in dmf_source[dmf_source["Risk"] == "High"].iterrows():
        rows.append(
            {
                "Question": f"Please provide source text and confirmed value for {row['DMF section']}.",
                "Triggered by": f"DMF source input: {row['Status']} / {row['Risk']} risk",
                "Evidence needed": row["Expected information"],
                "CTD update": row["DP linkage"],
                "Owner": "API supplier / CMC RA",
            }
        )
    for _, row in ctd_documents[ctd_documents["Risk"] == "High"].iterrows():
        rows.append(
            {
                "Question": f"Please provide source evidence and confirmed value for {row['CTD part']}.",
                "Triggered by": f"CTD document input: {row['Status']} / {row['Risk']} risk",
                "Evidence needed": row["Expected information"],
                "CTD update": row["CTD part"],
                "Owner": row["Owner"],
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
    for _, row in validation[validation["Gate"] == "Review"].head(10).iterrows():
        rows.append(
            {
                "Question": f"Please provide raw data and sample-preparation rationale for {row['Test item']} - {row['Item']}.",
                "Triggered by": f"Validation gate review: {row['Result']} {row['Unit']} / rule {row['Rule']}",
                "Evidence needed": str(row["Note"]),
                "CTD update": str(row["CTD update"]),
                "Owner": "Analytical / CMC RA",
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


def localize_markdown_packet(packet: str, lang: str) -> str:
    if lang != "ko":
        return packet
    replacements = {
        "# ToxiGuard Platform Ver.3 CMC RA Decision Packet": "# ToxiGuard Platform Ver.3 CMC RA 판단 패킷",
        "Generated:": "생성일:",
        "## Product Context": "## 제품 개요",
        "## Decision Gate": "## 판단 Gate",
        "## Product-Profile-Driven Questions": "## 제품 프로필 기반 검토 질문",
        "## Document Application Logic": "## 문서 적용 로직",
        "## Key Decision Points": "## 핵심 판단 포인트",
        "## Client CTD Intake Snapshot": "## 고객 CTD 접수 Snapshot",
        "## High-Risk DMF Source Inputs": "## 고위험 DMF 원문 입력",
        "## High-Risk CTD Source Inputs": "## 고위험 CTD 원문 입력",
        "## Long Source-Document Notes": "## 긴 원문 메모",
        "## High-Risk CTD Evidence": "## 고위험 CTD 근거",
        "## High-Risk Specification Rationale": "## 고위험 기준설정 근거",
        "## High-Risk DMF-to-DP Bridge": "## 고위험 DMF-to-DP Bridge",
        "## Calculation / Validation Snapshot": "## 계산 / 밸리데이션 Snapshot",
        "## Response Memo Seed": "## RA 답변 메모 Seed",
        "## Expert Review Boundary": "## 전문가 검토 한계",
        "## ICH Q14 Analytical Procedure Development Check": "## ICH Q14 분석법 개발 검토",
        "## Test-Specific Validation Summary": "## 시험항목별 밸리데이션 요약",
        "### Related Substance PDE/TDI Basis": "### 유연물질 PDE/TDI 근거",
        "### ICH Q3D Elemental Impurity Scope": "### ICH Q3D 금속불순물 범위",
        "### Validation Items Needing Review": "### 검토가 필요한 밸리데이션 항목",
        "| Profile signal | Evidence impact | CTD section | Risk question |": "| 제품 프로필 신호 | 근거 영향 | CTD 항목 | 리스크 질문 |",
        "| Review stage | Input document | What to capture | Where to apply | Decision point | CMC risk if unclear | Output artifact | Status | Risk | Action |": "| 검토 단계 | 입력 문서 | 확인할 정보 | 적용 위치 | 판단 포인트 | 불명확할 때의 CMC 리스크 | 산출물 | 상태 | 리스크 | 조치 |",
        "| Priority | Source area | Source item | Key point | Why it matters | Evidence required | Affected CTD | Suggested action | User decision |": "| 우선순위 | 근거 영역 | 근거 항목 | 핵심 포인트 | 중요한 이유 | 필요 근거 | 영향 CTD | 제안 조치 | 사용자 판단 |",
        "| DMF section | Expected information | Document source | Confirmed value | DP linkage | Action |": "| DMF 항목 | 필요 정보 | 문서 출처 | 확인값 | 완제 연결성 | 조치 |",
        "| CTD module | CTD part | Expected information | Confirmed value | Evidence use | Next action |": "| CTD 모듈 | CTD 파트 | 필요 정보 | 확인값 | 근거 활용 | 다음 조치 |",
        "| CTD module | CTD section | Status | Owner | Next action |": "| CTD 모듈 | CTD 항목 | 상태 | 담당 | 다음 조치 |",
        "| Test item | Acceptance criterion | Rationale basis | Reviewer question |": "| 시험항목 | 기준 | 설정 근거 | 심사자 질문 |",
        "| DMF element | DP impact | Action |": "| DMF 요소 | 완제 영향 | 조치 |",
        "| Question | Triggered by | Evidence needed | CTD update | Owner |": "| 질문 | 발생 원인 | 필요 근거 | CTD 수정 | 담당 |",
        "No high-risk item currently listed.": "현재 표시할 고위험 항목은 없습니다.",
        "No long source-document excerpt has been entered yet.": "아직 긴 원문 발췌가 입력되지 않았습니다.",
        "This packet is a decision-support draft. It does not replace CMC, analytical, regulatory, toxicology, clinical, legal, or quality expert review.": "이 패킷은 의사결정 보조 초안입니다. CMC, 분석, 규제, 독성, 임상, 법무 또는 품질 전문가 검토를 대체하지 않습니다.",
    }
    translated = packet
    for source, target in {**CONTENT_KO, **replacements}.items():
        translated = translated.replace(source, target)
    for source, target in VALUE_KO.items():
        translated = translated.replace(f"| {source} |", f"| {target} |")
        translated = translated.replace(f": **{source}**", f": **{target}**")
    return translated


def markdown_document_notes() -> str:
    notes = st.session_state.get("document_notes", {})
    if not isinstance(notes, dict) or not any(str(value).strip() for value in notes.values()):
        return "No long source-document excerpt has been entered yet.\n"
    labels = {
        "dmf": "DMF source note",
        "ctd_s": "CTD 3.2.S source note",
        "ctd_p": "CTD 3.2.P source note",
        "ctd_other": "Other CTD module note",
    }
    blocks = []
    for key, label in labels.items():
        text = str(notes.get(key, "")).strip()
        if text:
            blocks.append(f"### {label}\n\n{text}\n")
    return "\n".join(blocks)


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
    dmf_source = st.session_state.dmf_source_df
    ctd_documents = st.session_state.ctd_document_df
    document_logic = st.session_state.get("document_logic_df", pd.DataFrame(default_document_logic_rows()))
    decision_points = st.session_state.get("document_decision_df", document_decision_points(profile))
    if not isinstance(decision_points, pd.DataFrame) or decision_points.empty:
        decision_points = document_decision_points(profile)
    validation = validation_review_frame(include_gate=True)
    validation_summary = validation_summary_frame()
    intake_readiness = score_intake(intake)
    readiness = score_evidence(evidence)
    ctd_document_readiness = score_document_inputs(ctd_documents)
    dmf_document_readiness = score_document_inputs(dmf_source)
    combined_readiness = round((intake_readiness + readiness + ctd_document_readiness + dmf_document_readiness) / 4, 1)
    high_risks = count_high_risks(intake, evidence, spec, dmf, dmf_source, ctd_documents)
    gate, message = decision_gate(combined_readiness, high_risks)
    calc = st.session_state.get("last_calc", {})
    risk_notes = st.session_state.get("last_risk_notes", ["Run Calculation / Validation tab to generate LOD/LOQ and intercept notes."])

    intake_focus = intake_focus_rows(intake)
    high_evidence = evidence[evidence["Risk"] == "High"]
    high_spec = spec[spec["Risk"] == "High"]
    high_dmf = dmf[dmf["Risk"] == "High"]
    high_dmf_source = dmf_source[dmf_source["Risk"] == "High"]
    high_ctd_documents = ctd_documents[ctd_documents["Risk"] == "High"]
    review_validation = validation[validation["Gate"] == "Review"]

    return f"""# ToxiGuard Platform Ver.3 CMC RA Decision Packet

Generated: {date.today().isoformat()}

## Product Context

| Field | Value |
| --- | --- |
| Product | {profile['product']} |
| Active substance / API | {profile['active_substance']} |
| API supplier / DMF holder | {profile['api_supplier']} |
| Dosage form | {profile['dosage']} |
| Formulation technology / platform | {profile['formulation_platform']} |
| Strength | {profile['strength']} |
| Route | {profile['route']} |
| Clinical trial material / batch | {profile['clinical_material']} |
| Reference / comparator | {profile['reference']} |
| Target regions | {profile['target_regions']} |
| Lifecycle stage | {profile['stage']} |

## Decision Gate

- Gate: **{gate}**
- Client intake readiness: **{intake_readiness}%**
- CTD document readiness: **{ctd_document_readiness}%**
- DMF document readiness: **{dmf_document_readiness}%**
- 3.2.S/P evidence readiness: **{readiness}%**
- Combined readiness: **{combined_readiness}%**
- Open high risks: **{high_risks}**
- Interpretation: {message}

## Product-Profile-Driven Questions

{markdown_table(product_profile_prompts(profile), ["Profile signal", "Evidence impact", "CTD section", "Risk question"])}

## Document Application Logic

{markdown_table(document_logic, ["Review stage", "Input document", "What to capture", "Where to apply", "Decision point", "CMC risk if unclear", "Output artifact", "Status", "Risk", "Action"])}

## Key Decision Points

{markdown_table(decision_points, ["Priority", "Source area", "Source item", "Key point", "Why it matters", "Evidence required", "Affected CTD", "Suggested action", "User decision"])}

## Client CTD Intake Snapshot

{markdown_table(intake_focus, ["Intake area", "Client question", "Expected client document", "Risk", "CTD update direction"])}

## High-Risk DMF Source Inputs

{markdown_table(high_dmf_source, ["DMF section", "Expected information", "Document source", "Confirmed value", "DP linkage", "Action"])}

## High-Risk CTD Source Inputs

{markdown_table(high_ctd_documents, ["CTD module", "CTD part", "Expected information", "Confirmed value", "Evidence use", "Next action"])}

## Long Source-Document Notes

{markdown_document_notes()}

## High-Risk CTD Evidence

{markdown_table(high_evidence, ["CTD module", "CTD section", "Status", "Owner", "Next action"])}

## High-Risk Specification Rationale

{markdown_table(high_spec, ["Test item", "Acceptance criterion", "Rationale basis", "Reviewer question"])}

## High-Risk DMF-to-DP Bridge

{markdown_table(high_dmf, ["DMF element", "DP impact", "Action"])}

## Calculation / Validation Snapshot

- Last reviewed test item: {calc.get('test_item', 'Not run')}
- Reference concentration: {format_report_number(calc.get('reference_conc', 'Not run'))} {calc.get('unit', '')}
- Actual final concentration: {format_report_number(calc.get('final_conc', 'Not run'))} {calc.get('unit', '')}
- Target concentration: {format_report_number(calc.get('target_conc', 'Not run'))} {calc.get('unit', '')}
- Actual vs target difference: {format_report_diff(calc.get('diff_pct', 'Not run'))}

### Test-Specific Validation Summary

{markdown_table(validation_summary, ["Test item", "Gate", "Review items", "Regulatory basis", "CTD update"])}

### LOD / LOQ / Intercept Notes

{chr(10).join(f"- {note}" for note in risk_notes)}

### Validation Items Needing Review

{markdown_table(review_validation, ["Test item", "Item", "Result", "Unit", "Rule", "Lower", "Upper", "Note", "CTD update"])}

## Response Memo Seed

{markdown_table(response_rows(), ["Question", "Triggered by", "Evidence needed", "CTD update", "Owner"])}

## Expert Review Boundary

This packet is a decision-support draft. It does not replace CMC, analytical, regulatory, toxicology, clinical, legal, or quality expert review.
"""


def render_response(lang: str, profile: dict[str, Any]) -> None:
    section_header(tr(lang, "response"), tr(lang, "response_help"), "file_pen", "green")
    rows = response_rows()
    st.dataframe(display_dataframe(rows, lang), width="stretch", hide_index=True)
    packet = localize_markdown_packet(build_decision_packet(profile), lang)
    mini_heading(tr(lang, "packet_preview"), "file_pen", "green")
    st.text_area(tr(lang, "markdown_preview"), value=packet, height=360)
    st.download_button(
        tr(lang, "download"),
        data=packet,
        file_name="ToxiGuard_VCC_CMC_RA_Decision_Packet.md",
        mime="text/markdown",
    )


def render_launcher(lang: str) -> None:
    section_header(
        tr(lang, "launcher"),
        "Open connected ToxiGuard apps and plan the next evidence workbench modules."
        if lang == "en"
        else "연결된 ToxiGuard 앱을 열고 다음 evidence workbench 모듈을 계획합니다.",
        "database",
        "blue",
    )
    mini_heading(tr(lang, "available_apps"), "database", "blue")
    launcher_cards = [
        ("ToxiGuard-SOP Gate", "Calculation / Validation Review" if lang == "en" else "계산 / 밸리데이션 검토", "calculator", "orange"),
        ("Clinical Trial Intelligence", "Clinical evidence layer" if lang == "en" else "임상 근거 레이어", "trend", "teal"),
        ("Revenue Forecast Intelligence", "Business evidence layer" if lang == "en" else "비즈니스 근거 레이어", "gauge", "green"),
        ("ToxiGuard-MediLens", "Medication label safety evidence layer" if lang == "en" else "의약품 라벨 기반 복약 안전성 근거 레이어", "shield", "blue"),
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
            {
                "App": "ToxiGuard-MediLens",
                "Role": "Medication label, side-effect, food, and condition guidance",
                "Run": "https://github.com/lyn0109-Toxi/ToxiGuard-MediLens",
            },
        ]
    )
    st.dataframe(display_dataframe(available, lang), width="stretch", hide_index=True)
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
    st.dataframe(display_dataframe(next_builds, lang), width="stretch", hide_index=True)


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
    requested_lang = requested_language_key()
    if st.session_state.get("lang") != requested_lang:
        st.session_state.lang = requested_lang
    with st.sidebar:
        lang_label = st.radio(
            tr(st.session_state.lang, "language"),
            ["한국어", "English"],
            index=1 if st.session_state.lang == "en" else 0,
            horizontal=True,
        )
        lang = "ko" if lang_label == "한국어" else "en"
        st.session_state.lang = lang
        if requested_language_key() != lang:
            st.query_params["lang"] = lang
    profile = render_sidebar(st.session_state.lang)
    render_header(st.session_state.lang)
    page_key = current_page_key()
    render_icon_nav(st.session_state.lang, page_key)
    render_selected_page(page_key, st.session_state.lang, profile)


if __name__ == "__main__":
    main()

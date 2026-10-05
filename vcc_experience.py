"""Purpose, orientation, and task guidance for the existing VCC workbench."""
from html import escape
from typing import Callable

import streamlit as st


COPY = {
    "ko": {
        "audience": "CMC · RA 담당자와 컨설턴트를 위한 검토 도구",
        "title": "기준농도부터 문서 근거까지,<br>밸리데이션 검토를 한곳에서",
        "description": "기준농도와 실제 시료 제조값을 연결하고, 가이드라인에 맞춰 검토 기준을 조정하세요. 문서 근거와 CTD 보완사항도 함께 정리할 수 있습니다.",
        "input": "입력하는 것", "input_detail": "시료 제조값 · 시험 결과 · 검토 기준 · DMF·CTD 문서 근거",
        "output": "얻는 결과", "output_detail": "농도 계산 · 밸리데이션 점검 · 문서 보완사항 · 검토 메모",
        "start": "문서 검토 시작", "validation_start": "계산·밸리데이션 검토 시작", "preview": "결과물 먼저 보기",
        "sample_note": "예시 제품과 자료가 미리 채워져 있습니다. 직접 수정하며 흐름을 확인할 수 있습니다.",
        "process": "검토 목적에 따라 시작하세요",
        "steps": [("01", "농도·시료 제조 계산", "함량·유연물질·용출 등 시험항목별 기준농도와 실제 제조값을 연결하고 LOD·LOQ·직선성을 확인합니다."), ("02", "가이드라인·밸리데이션", "판정 규칙과 허용기준을 조정하며 검토합니다. Q14 체크리스트, Q3D 범위, PDE/TDI 근거를 확인합니다."), ("03", "문서·CTD 근거 검토", "문서 접수와 원문, CTD 근거 맵, P.5.6 규격 근거, DMF 연결성을 검토하고 메모로 내려받습니다.")],
        "example": "결과물 예시", "example_title": "문서의 빈틈을 다음 행동으로",
        "example_rows": [("발견한 빈틈", "DMF의 최신 버전과 참조 권한 확인이 필요합니다."), ("고객에게 물을 질문", "현재 LoA와 해당 제품에 적용한 DMF 버전 이력을 제공할 수 있나요?"), ("보완할 위치", "CTD 3.2.S 참조 근거 · 원료와 완제의 연결성")],
        "scope": "어디까지 도와주나요?",
        "scope_text": "입력한 제조값·시험 결과로 계산을 확인하고, 조정 가능한 판정 규칙과 허용기준으로 밸리데이션을 검토합니다. 문서 상태·원문·확인값은 고객 질문과 CTD 보완 초안으로 연결됩니다. 계산·가이드라인 점검과 문서 검토 결과를 하나의 메모로 내려받을 수 있습니다.",
        "session": "작업 내용은 현재 접속 세션에 유지됩니다. 새로고침이나 접속 종료 전에 검토 메모를 내려받으세요.",
        "sample_banner": "예시에서 시작한 검토 초안 · 기본 제품·문서 상태·시험 수치는 예시입니다. 실제 자료로 수정하고 출처를 확인하세요.",
        "score_note": "준비도와 검토 상태는 입력값을 요약한 내부 점검 지표입니다. 규제기관의 평가나 허가 가능성을 뜻하지 않습니다.",
    },
    "en": {
        "audience": "A review tool for CMC / RA teams and consultants",
        "title": "Connect concentrations, validation<br>and document evidence",
        "description": "Connect reference concentrations to actual sample preparations, adjust review criteria for your guideline context, and bring document evidence and CTD actions into one review.",
        "input": "What you provide", "input_detail": "Preparation values · test results · review criteria · DMF / CTD evidence",
        "output": "What you take away", "output_detail": "Concentration calculations · validation checks · document actions · review memo",
        "start": "Start document review", "validation_start": "Start calculation and validation", "preview": "Preview the output",
        "sample_note": "A sample product and document set are prefilled. Edit them to explore the workflow.",
        "process": "Start with the review you need",
        "steps": [("01", "Concentration and preparation", "Connect reference concentrations to actual preparations for assay, related substances, dissolution and other tests. Check LOD, LOQ and linearity."), ("02", "Guidelines and validation", "Adjust review rules and acceptance limits. Check Q14 development evidence, Q3D scope and the PDE/TDI basis."), ("03", "Documents and CTD evidence", "Review document intake, source excerpts, CTD evidence, P.5.6 rationale and DMF linkage, then download the memo.")],
        "example": "Example output", "example_title": "From a document gap to a next action",
        "example_rows": [("Evidence gap", "The current DMF version and right of reference need confirmation."), ("Question for the client", "Can you provide the current LoA and the DMF version history used for this product?"), ("CTD action", "CTD 3.2.S reference evidence · API-to-drug-product linkage")],
        "scope": "What does VCC help with?",
        "scope_text": "Check calculations using preparation values and test results, and review validation with editable rules and acceptance limits. Document statuses, source excerpts and confirmed values feed client questions and CTD actions. Download calculation, guideline and document review results in one memo.",
        "session": "Work is kept in this browser session. Download your memo before refreshing or ending the session.",
        "sample_banner": "Review draft started from examples · Default product details, document statuses, and test values are examples. Replace them with your evidence and verify the sources.",
        "score_note": "Readiness and review states summarize your inputs for internal review. They are not regulatory assessments or approval probabilities.",
    },
}

STYLE = """
<style>
.block-container {max-width:1220px; padding-top:4.5rem; padding-bottom:3rem;}
.vcc-brand {font-size:1.2rem; font-weight:800; letter-spacing:-.03em; color:#163945; padding:12px 0;}
.vcc-brand small {font-size:.68rem; font-weight:600; letter-spacing:.12em; color:#53777b; margin-left:12px;}
.vcc-hero {background:#143642; border-radius:20px; padding:44px 42px; color:#fff; margin:8px 0 18px;}
.vcc-eyebrow {color:#ace2d9; font-size:.8rem; font-weight:600; letter-spacing:.03em;}
.vcc-hero h1 {color:#fff; font-size:clamp(1.8rem,3.5vw,2.8rem); line-height:1.3; letter-spacing:-.045em; margin:15px 0; padding:0;}
.vcc-hero>p {color:#e1edec; max-width:790px; font-size:1rem; line-height:1.8;}
.vcc-io {display:grid; grid-template-columns:1fr 1fr; gap:28px; border-top:1px solid #466570; margin-top:26px; padding-top:20px;}
.vcc-io strong {display:block; color:#a9dfd1; font-size:.8rem; margin-bottom:7px;}
.vcc-io span {font-size:.92rem; color:#f2f7f6; line-height:1.6;}
.vcc-steps {display:grid; grid-template-columns:repeat(3,1fr); gap:16px; margin:16px 0 28px;}
.vcc-step {border:1px solid #d7e3e3; border-radius:14px; padding:22px; background:#fff; color:#173846;}
.vcc-step b {color:#39877e; font-size:.77rem; letter-spacing:.1em;}
.vcc-step h3 {font-size:1.1rem; color:#173846; margin:12px 0 9px; padding:0;}
.vcc-step p {font-size:.9rem; color:#526973; margin:0; line-height:1.7;}
.vcc-output {border:1px solid #d5e3e0; border-radius:16px; padding:24px 28px; background:#f1f7f5; color:#173846;}
.vcc-output small {font-size:.73rem; color:#427e75; font-weight:700;}
.vcc-output h3 {color:#173846; margin:8px 0 15px; padding:0; font-size:1.22rem;}
.vcc-output-row {display:grid; grid-template-columns:145px 1fr; gap:16px; padding:13px 0; border-top:1px solid #d7e4df; font-size:.92rem; line-height:1.65;}
.vcc-output-row strong {color:#356b63;}
.vcc-guidance {border-left:3px solid #429387; padding:8px 16px; margin:4px 0 16px; color:inherit;}
.vcc-guidance strong {display:block; margin-bottom:5px;}
.vcc-guidance span {font-size:.9rem; line-height:1.65;}
@media(max-width:640px) {
.block-container {padding-top:4rem; padding-left:1rem; padding-right:1rem;}
.vcc-hero {padding:27px 22px; border-radius:14px;}
.vcc-hero h1 {font-size:1.75rem;}
.vcc-io,.vcc-steps {grid-template-columns:1fr; gap:15px;}
.vcc-output {padding:22px;}
.vcc-output-row {grid-template-columns:1fr; gap:4px;}
.vcc-brand small {display:block; margin:4px 0 0;}
}
</style>
"""


def render_landing(lang: str, go_to_page: Callable, language_selector: Callable) -> None:
    c = COPY[lang]
    st.markdown(STYLE, unsafe_allow_html=True)
    brand, language = st.columns([2, 1])
    with brand:
        st.markdown('<div class="vcc-brand">ToxiGuard VCC <small>VALIDATION & CMC REVIEW</small></div>', unsafe_allow_html=True)
    with language:
        language_selector(lang)
    st.markdown(
        f'<section class="vcc-hero"><div class="vcc-eyebrow">{c["audience"]}</div>'
        f'<h1>{c["title"]}</h1><p>{c["description"]}</p><div class="vcc-io">'
        f'<div><strong>{c["input"]}</strong><span>{c["input_detail"]}</span></div>'
        f'<div><strong>{c["output"]}</strong><span>{c["output_detail"]}</span></div></div></section>',
        unsafe_allow_html=True,
    )
    start, validation, preview = st.columns([1, 1.3, 1])
    start.button(c["start"], key="landing_enter_button", type="primary", width="stretch", on_click=go_to_page, args=("intake",))
    validation.button(c["validation_start"], key="landing_validation_button", type="primary", width="stretch", on_click=go_to_page, args=("validation",))
    preview.button(c["preview"], key="landing_preview_button", width="stretch", on_click=go_to_page, args=("response",))
    st.caption(c["sample_note"])
    st.button("Telmisartan · NORA 연계 사례" if lang == "ko" else "Telmisartan · NORA linked case", key="landing_case_button", width="stretch", on_click=go_to_page, args=("case",))
    st.subheader(c["process"])
    st.markdown('<div class="vcc-steps">'+''.join(
        f'<article class="vcc-step"><b>{number}</b><h3>{title}</h3><p>{note}</p></article>'
        for number, title, note in c["steps"])+"</div>", unsafe_allow_html=True)
    st.markdown(f'<section class="vcc-output"><small>{c["example"]}</small><h3>{c["example_title"]}</h3>'+''.join(
        f'<div class="vcc-output-row"><strong>{label}</strong><span>{text}</span></div>'
        for label, text in c["example_rows"])+"</section>", unsafe_allow_html=True)
    with st.expander(c["scope"]):
        st.write(c["scope_text"])
        st.caption(c["session"])
    from feedback import render_feedback
    render_feedback(lang)


GUIDANCE = {
    "intake": (("받은 파일을 섹션에 연결하고, 누락된 자료를 요청하세요.", "DMF·CTD 파일을 등록하면 접수 현황이 갱신됩니다. ‘추가자료 요청’에서 고객에게 필요한 자료·담당자·기한을 정리하세요."), ("Link received files to sections and request missing documents.", "Register DMF / CTD files to update receipt. Use Information requests to organize needed documents, owners and due dates.")),
    "documents": (("접수한 원문을 확인하고 판단 근거를 기록하세요.", "파일 접수·누락 현황을 확인한 뒤 ‘원문·확인값 검토’에서 발췌문과 확인값을 기록하고 근거 맵에 적용하세요."), ("Review the received sources and record the evidence.", "Check file receipt and missing sections, then record excerpts and confirmed values in Source and confirmed-value review before applying them to the evidence map.")),
    "dashboard": (("부족한 근거와 우선 확인할 질문을 정리하세요.", "준비도 숫자보다 미해결 항목과 필요한 근거를 먼저 확인하세요. 세부 검토 화면에서 원문·규격·원료 연결성을 검토할 수 있습니다."), ("Prioritize evidence gaps and questions.", "Review unresolved items and evidence requests alongside the scores. Use detailed views for sources, specifications, and API linkage.")),
    "evidence": (("각 CTD 항목을 근거·담당자·다음 행동에 연결하세요.", "출처를 확인한 항목만 상태를 갱신하고, 근거가 부족하면 필요한 자료와 담당자를 기록하세요."), ("Connect each CTD section to evidence and an owner.", "Update status after checking the source. Record the required evidence, owner, and next action for gaps.")),
    "spec": (("규격의 숫자에 설정 근거가 있는지 검토하세요.", "시험항목별 기준, 시험법, 근거 자료를 확인하고 보완할 질문을 기록하세요."), ("Check the evidence behind each specification.", "Review criteria, methods, and supporting evidence, then record unresolved questions.")),
    "dmf": (("원료 자료가 완제의 품질 근거로 연결되는지 확인하세요.", "DMF 항목별 공급자 근거와 신청자 확인 상태를 검토하고 필요한 조치를 정리하세요."), ("Check how API evidence supports the drug product.", "Review supplier evidence, applicant verification, and follow-up actions for each DMF element.")),
    "validation": (("시험항목을 선택하고 실제 수치로 계산을 확인하세요.", "시료 제조 조건과 결과를 입력하고, 판정 규칙·허용기준을 조정하세요. 아래에서 Q14, 유연물질 PDE/TDI, Q3D 등 해당 시험의 검토 항목을 확인할 수 있습니다."), ("Choose a test and check the actual values.", "Enter preparation conditions and results, then adjust review rules and acceptance limits. Review Q14, related-substance PDE/TDI, Q3D and other checks for the selected test below.")),
    "response": (("고객 질문과 CTD 보완사항을 메모로 가져가세요.", "아래 초안에서 출처·담당자·보완 위치를 확인하세요. 검토 메모에는 현재 입력값과 계산 검토 결과가 함께 담깁니다."), ("Take client questions and CTD actions into your meeting.", "Review sources, owners, and CTD locations in the draft. The memo includes current inputs and calculation review results.")),
}


def render_guidance(page: str, lang: str) -> None:
    if page not in GUIDANCE:
        return
    title, detail = GUIDANCE[page][0 if lang == "ko" else 1]
    st.markdown(f'<div class="vcc-guidance"><strong>{escape(title)}</strong><span>{escape(detail)}</span></div>', unsafe_allow_html=True)

"""Session-scoped customer files and section-specific information requests."""
from __future__ import annotations

from datetime import date
import hashlib
from html import escape
from typing import Callable

import pandas as pd
import streamlit as st

import document_intake as intake


STATE_KEY = "customer_document_intake"


def bi(lang: str, ko: str, en: str) -> str:
    return ko if lang == "ko" else en


def get_state() -> dict:
    if STATE_KEY not in st.session_state:
        st.session_state[STATE_KEY] = intake.new_intake()
    return st.session_state[STATE_KEY]


def section_label(section_id: str, lang: str) -> str:
    item = next(row for row in intake.SECTION_CATALOG if row["id"] == section_id)
    prefix = "DMF" if item["group"] == "DMF" else "CTD"
    return f"{prefix} {item['code']} · {item['label_ko' if lang == 'ko' else 'label_en']}"


def display_rows(state: dict, lang: str) -> pd.DataFrame:
    statuses = {"정보없음": "No information", "검토대기": "Awaiting review",
                "추가자료요청": "Additional information requested", "해당없음": "Not applicable"}
    return pd.DataFrame([{
        bi(lang, "섹션", "Section"): section_label(row["section_id"], lang),
        bi(lang, "접수 현황", "Receipt"): (bi(lang, "해당없음", "Not applicable") if row["status"] == "해당없음"
            else bi(lang, "파일 접수", "Files received") if row["file_count"] else bi(lang, "정보없음", "No information")),
        bi(lang, "검토 상태", "Review state"): row["status"] if lang == "ko" else statuses[row["status"]],
        bi(lang, "파일 수", "Files"): row["file_count"],
        bi(lang, "파일명", "File names"): row["file_names"],
    } for row in intake.summary_rows(state)])


def request_frame(state: dict, lang: str) -> pd.DataFrame:
    return pd.DataFrame([{
        bi(lang, "섹션", "Section"): section_label(row["section_id"], lang),
        bi(lang, "접수 현황", "Receipt"): bi(lang, "파일 접수", "Files received") if row["file_count"] else bi(lang, "정보없음", "No information"),
        bi(lang, "요청 내용", "Information requested"): row["request"],
        bi(lang, "담당자", "Owner"): row["owner"],
        bi(lang, "요청 기한", "Due date"): row["due_date"],
        bi(lang, "우선순위", "Priority"): row["priority"] if lang == "ko" else {"높음": "High", "보통": "Normal", "낮음": "Low"}[row["priority"]],
    } for row in intake.request_rows(state, lang=lang)])


def _markdown_table(frame: pd.DataFrame) -> str:
    def clean(value):
        return escape(str(value), quote=False).replace("|", "\\|").replace("\r", " ").replace("\n", "<br>")
    if frame.empty:
        return "—"
    return "\n".join(["| " + " | ".join(map(clean, frame.columns)) + " |",
                      "| " + " | ".join("---" for _ in frame.columns) + " |",
                      *["| " + " | ".join(map(clean, row)) + " |" for row in frame.itertuples(index=False, name=None)]])


def request_document(state: dict, lang: str, product: str = "") -> str:
    title = bi(lang, "고객 추가자료 요청서", "Customer information request")
    context = bi(lang, "제품", "Product")
    intro = bi(lang, "아래 섹션의 자료 또는 보완 설명을 부탁드립니다. 해당하지 않는 항목은 사유를 알려주세요.",
               "Please provide the documents or clarifications below. Explain any sections that do not apply.")
    linked = source_request_frame(state, lang)
    extra = ("\n## " + bi(lang, "원문 근거에서 연결한 추가자료", "Additional information linked to source evidence")
             + "\n\n" + _markdown_table(linked) + "\n") if not linked.empty else ""
    return f"# {title}\n\n{context}: {escape(product, quote=False)}\n\n{intro}\n\n{_markdown_table(request_frame(state, lang))}\n{extra}"


def source_request_frame(state: dict, lang: str) -> pd.DataFrame:
    from document_trace_ui import get_trace
    from document_trace import source_label
    trace = get_trace(state["files"])
    return pd.DataFrame([{bi(lang, "문서·버전", "Document / version"): state["files"][item["file_id"]]["name"] + " / " + item["document_snapshot"].get("version", ""),
                          bi(lang, "원문 위치", "Source location"): item["location"] + " / " + source_label(item["source_ref"]),
                          "CTD": item["ctd_target"], bi(lang, "추가자료", "Information needed"): item["request"],
                          bi(lang, "근거 상태", "Evidence state"): item["status"], bi(lang, "담당자", "Owner"): item["owner"],
                          bi(lang, "기한", "Due date"): item["due_date"]} for item in trace["evidence"] if item["request"]])


def intake_report(state: dict, lang: str = "ko") -> str:
    from document_trace import trace_report
    from document_trace_ui import get_trace
    from dosage_checklist import checklist_report
    profile = st.session_state.get("profile_values", {})
    return ("## " + bi(lang, "고객 파일 접수 현황", "Customer file receipt") + "\n\n"
            + bi(lang, "지원 섹션별 실제 업로드 현황입니다. 파일 접수는 내용 검토 완료를 뜻하지 않습니다. 기존 검토표의 예시 상태와 별도로 관리합니다.",
                 "Actual uploads for the supported sections. Receipt does not confirm the content. This inventory is separate from example review data.")
            + "\n\n" + _markdown_table(display_rows(state, lang)) + "\n\n## "
            + bi(lang, "누락·추가자료 요청", "Missing and additional information requests")
            + "\n\n" + _markdown_table(request_frame(state, lang)) + "\n"
            + trace_report(get_trace(state["files"]), state["files"], lang, profile)
            + checklist_report(profile, lang))


def render_uploads(lang: str) -> None:
    state = get_state()
    rows = intake.summary_rows(state)
    metrics = st.columns(3)
    metrics[0].metric(bi(lang, "등록 파일", "Registered files"), len(state["files"]))
    metrics[1].metric(bi(lang, "정보없는 섹션", "Sections without information"),
                      sum(not r["file_count"] and r["status"] != "해당없음" for r in rows))
    metrics[2].metric(bi(lang, "자료 요청 항목", "Information requests"), len(intake.request_rows(state, lang=lang)))
    st.caption(bi(lang, "고객 자료를 아래에서 직접 등록하세요. 등록하지 않은 섹션은 ‘정보없음’으로 시작합니다. 표는 지원하는 섹션 목록이며 제출요건의 완전성 판정은 아닙니다.",
        "Register customer documents below. Sections without a file start as No information. This is an inventory of supported sections, not a completeness assessment of submission requirements."))

    groups = list(dict.fromkeys(row["group"] for row in intake.SECTION_CATALOG))
    group = st.selectbox(bi(lang, "자료 구분", "Document group"), groups, key="doc_intake_group")
    ids = [row["id"] for row in intake.SECTION_CATALOG if row["group"] == group]
    section = st.selectbox(bi(lang, "업로드할 섹션", "Upload section"), ids,
                           format_func=lambda x: section_label(x, lang), key=f"doc_intake_section_{group}")
    all_ids = [row["id"] for row in intake.SECTION_CATALOG]
    with st.form(f"doc_intake_upload_form_{section}", clear_on_submit=True):
        files = st.file_uploader(bi(lang, "고객 DMF·CTD 파일", "Customer DMF / CTD files"),
            type=["pdf", "docx", "xlsx", "txt", "doc", "xls"], accept_multiple_files=True,
            key=f"doc_intake_upload_{section}")
        extra = st.multiselect(bi(lang, "같은 파일을 함께 연결할 섹션 (선택)", "Also link these files to sections (optional)"),
            [x for x in all_ids if x != section], format_func=lambda x: section_label(x, lang),
            key=f"doc_intake_extra_{section}")
        st.caption(bi(lang, "파일당 20 MB, 세션 전체 100 MB·최대 50개. 통합 문서는 실제 해당 섹션에만 연결하세요.",
            "20 MB per file; 100 MB and 50 files per session. Link combined documents only to sections they cover."))
        submitted = st.form_submit_button(bi(lang, "선택 섹션에 파일 등록", "Register files for selected sections"), type="primary")
    if submitted:
        if not files:
            st.error(bi(lang, "등록할 파일을 선택하세요.", "Select a file to register."))
        else:
            try:
                candidate = state
                for upload in files:
                    candidate = intake.add_file(candidate, upload.name, upload.getvalue(), [section, *extra], upload.type)
                st.session_state[STATE_KEY] = candidate
                st.session_state["doc_insights_file"] = hashlib.sha256(files[-1].getvalue()).hexdigest()
                st.session_state["doc_intake_notice"] = bi(lang, "파일을 등록했습니다. 내용을 확인한 뒤 필요한 보완자료를 요청하세요.",
                    "Files registered. Review the contents and request any further information needed.")
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))
    if notice := st.session_state.pop("doc_intake_notice", ""):
        st.success(notice)
    st.info(bi(lang, "파일과 추출 결과는 VCC 서버의 현재 접속 세션에서만 관리됩니다. 새로고침·접속 종료·서버 재시작 시 사라질 수 있으므로 원본은 따로 보관하세요. ‘문서 분석’에서 PDF·DOCX·XLSX·TXT의 추출 근거를 확인할 수 있습니다. 자동 추출은 검토 완료를 의미하지 않습니다.",
        "Files and extracted results are held in the current session on the VCC server. Keep your originals: refresh, disconnect or server restart may clear the session. Inspect extracted PDF, DOCX, XLSX and TXT evidence in Document insights. Extraction does not mean review is complete."))
    st.subheader(bi(lang, "섹션별 접수 현황", "Receipt by section"))
    st.dataframe(display_rows(state, lang), hide_index=True, width="stretch", height=420)
    if state["files"]:
        with st.expander(bi(lang, "등록 파일 확인·섹션 변경", "Manage registered files and sections")):
            file_id = st.selectbox(bi(lang, "등록 파일 선택", "Select registered file"), list(state["files"]),
                format_func=lambda x: state["files"][x]["name"], key="doc_intake_file")
            item = state["files"][file_id]
            st.caption(f"{item['name']} · {item['size'] / 1024:.1f} KB")
            st.download_button(bi(lang, "원본 내려받기", "Download original"), item["content"], file_name=item["name"],
                mime="application/octet-stream", key=f"doc_intake_original_{file_id}")
            with st.form(f"doc_intake_links_{file_id}"):
                links = st.multiselect(bi(lang, "연결 섹션", "Linked sections"), all_ids, default=item["section_ids"],
                    format_func=lambda x: section_label(x, lang), key=f"doc_intake_reassign_{file_id}")
                saved = st.form_submit_button(bi(lang, "섹션 연결 저장", "Save section links"))
            if saved:
                try:
                    st.session_state[STATE_KEY] = intake.reassign_file(state, file_id, links)
                    st.rerun()
                except ValueError as exc:
                    st.error(str(exc))
            if st.button(bi(lang, "이 파일 등록 해제", "Remove this file from the session"), key=f"doc_intake_remove_{file_id}"):
                st.session_state[STATE_KEY] = intake.delete_file(state, file_id)
                st.rerun()


def render_requests(lang: str, product: str = "", editable: bool = True) -> None:
    state = get_state()
    st.subheader(bi(lang, "누락·추가자료 요청", "Missing and additional information requests"))
    st.caption(bi(lang, "자료가 없는 섹션은 자동으로 요청 목록에 포함됩니다. 검토 중 발견한 보완사항, 담당자와 기한을 추가하세요. 요청서는 내려받아 검토한 뒤 고객에게 전달할 수 있습니다.",
        "Sections without files are automatically included. Add review findings, owners and due dates. Download and review the request before sharing it with the customer."))
    if editable:
        section = st.selectbox(bi(lang, "요청·적용 여부를 정리할 섹션", "Section to update"),
            [r["id"] for r in intake.SECTION_CATALOG], format_func=lambda x: section_label(x, lang), key="doc_intake_request_section")
        current = state["section_states"].get(section, {})
        row = next(r for r in intake.summary_rows(state) if r["section_id"] == section)
        choices = ["정보없음", "추가자료요청", "해당없음"] if not row["file_count"] else ["검토대기", "추가자료요청", "해당없음"]
        selected = row["status"] if row["status"] in choices else choices[0]
        labels = {"정보없음": "No information", "검토대기": "Awaiting review", "추가자료요청": "Request more information", "해당없음": "Not applicable"}
        with st.form(f"doc_intake_request_form_{section}_{lang}"):
            status = st.selectbox(bi(lang, "처리 상태", "Handling status"), choices, index=choices.index(selected),
                format_func=lambda x: x if lang == "ko" else labels[x], key=f"doc_intake_status_{section}_{lang}")
            note = st.text_area(bi(lang, "요청 내용 또는 해당없음 사유", "Request or reason for not applicable"),
                value=current.get("note", ""), key=f"doc_intake_note_{section}_{lang}",
                placeholder=bi(lang, "예: 최신 DMF 버전, 승인된 규격서 및 관련 시험법 밸리데이션 보고서를 제공해 주세요.",
                    "For example: provide the current DMF version, approved specification and method validation reports."))
            c1, c2, c3 = st.columns(3)
            owner = c1.text_input(bi(lang, "담당자", "Owner"), value=current.get("owner", ""), key=f"doc_intake_owner_{section}_{lang}")
            due = c2.date_input(bi(lang, "요청 기한", "Due date"), value=date.fromisoformat(current["due_date"]) if current.get("due_date") else None,
                key=f"doc_intake_due_{section}_{lang}")
            priorities = ["높음", "보통", "낮음"]
            priority = c3.selectbox(bi(lang, "우선순위", "Priority"), priorities,
                index=priorities.index(current.get("priority", "보통")),
                format_func=lambda x: x if lang == "ko" else {"높음": "High", "보통": "Normal", "낮음": "Low"}[x],
                key=f"doc_intake_priority_{section}_{lang}")
            saved = st.form_submit_button(bi(lang, "요청 내용 저장", "Save information request"))
        if saved:
            try:
                if status in {"추가자료요청", "해당없음"} and not note.strip():
                    raise ValueError(bi(lang, "추가자료 요청 내용 또는 해당없음 사유를 입력하세요.", "Enter the information requested or the reason this section does not apply."))
                st.session_state[STATE_KEY] = intake.set_section_state(state, section, status, note,
                    owner=owner, due_date=due.isoformat() if due else "", priority=priority)
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))
    frame = request_frame(state, lang)
    if frame.empty:
        st.success(bi(lang, "현재 요청 목록에 남은 항목이 없습니다. 내용 검토 완료를 의미하지는 않습니다.",
            "No outstanding information requests. This does not mean content review is complete."))
    else:
        st.dataframe(frame, hide_index=True, width="stretch", height=360)
    a, b = st.columns(2)
    a.download_button(bi(lang, "추가자료 요청 목록 (CSV)", "Information request list (CSV)"),
        intake.request_csv(state, lang=lang), file_name="VCC_information_requests.csv", mime="text/csv", key="doc_intake_request_csv")
    b.download_button(bi(lang, "고객 요청서 (문서)", "Customer request (document)"),
        request_document(state, lang, product), file_name="VCC_customer_information_request.md", mime="text/markdown", key="doc_intake_request_md")
    actions = source_request_frame(state, lang)
    if not actions.empty:
        st.markdown("#### " + bi(lang, "원문 근거에서 연결한 추가자료 요청", "Information requests linked to source evidence"))
        st.dataframe(actions, hide_index=True, width="stretch")


def render_workspace(lang: str, profile: dict, legacy: Callable[[], None], legacy_label: str) -> None:
    get_state()
    tabs = st.tabs([bi(lang, "섹션별 파일 접수", "Files by section"), bi(lang, "추가자료 요청", "Information requests"), legacy_label,
                    bi(lang, "문서 분석", "Document insights"),
                    bi(lang, "버전·출처 추적", "Versions and source trace"),
                    bi(lang, "제형별 검토", "Dosage-form checklist")])
    with tabs[0]:
        render_uploads(lang)
    with tabs[1]:
        render_requests(lang, profile.get("product", ""))
    with tabs[2]:
        st.info(bi(lang, "아래는 기존 검토표입니다. 초기 예시 상태는 실제 파일 접수와 별개입니다. 업로드한 원문에서 확인한 내용만 발췌·확인값으로 기록하세요.",
            "These are the existing review tables. Initial example statuses are separate from actual file receipt. Record excerpts and values only after checking the uploaded source."))
        legacy()
    with tabs[3]:
        from document_insights_ui import render_insights
        render_insights(get_state(), lang)
    with tabs[4]:
        from document_trace_ui import render_trace
        render_trace(get_state(), lang, profile)
    with tabs[5]:
        from dosage_checklist import render_checklist
        render_checklist(lang, profile)

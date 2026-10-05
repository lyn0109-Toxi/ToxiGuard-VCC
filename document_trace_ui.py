"""Document applicability, text-version differences and source-linked actions."""
from datetime import date
import json

import streamlit as st

from document_insights import extract_document
from document_trace import applicability, compare_documents, new_trace, prune_trace, save_document, save_evidence, source_label

STATE_KEY = "customer_document_trace"


def get_trace(files):
    st.session_state[STATE_KEY] = prune_trace(st.session_state.get(STATE_KEY, new_trace()), files)
    diff = st.session_state.get("trace_diff", {})
    if diff and (diff.get("old_id") not in files or diff.get("new_id") not in files):
        st.session_state.pop("trace_diff", None)
    return st.session_state[STATE_KEY]


def render_trace(state, lang, profile):
    def bi(ko, en):
        return ko if lang == "ko" else en
    st.subheader(bi("문서 버전·적용 범위", "Document versions and applicability"))
    st.caption(bi("출처와 적용 범위는 검토자가 확인해 기록합니다. 파일 접수와 텍스트 추출만으로 확인 상태가 바뀌지 않습니다.",
                  "Record the source and applicability after reviewer checks. Receipt and extraction do not change confirmation status."))
    files = state["files"]
    trace = get_trace(files)
    if not files:
        st.info(bi("파일을 먼저 등록하세요.", "Register a file first."))
        return
    file_id = st.selectbox(bi("출처를 기록할 문서", "Document to trace"), list(files),
                          format_func=lambda key: files[key]["name"], key="trace_file")
    current = trace["documents"].get(file_id, {})
    with st.form(f"trace_metadata_{file_id}_{lang}"):
        version = st.text_input(bi("문서 / 시험법 버전", "Document / method version"), current.get("version", ""))
        system = st.selectbox(bi("문서 관리 시스템", "Source system"), ["", "LIMS", "QC RDM", "DMF", "Supplier", "Other"],
                             index=["", "LIMS", "QC RDM", "DMF", "Supplier", "Other"].index(current.get("system", "")))
        source = st.text_input(bi("출처·문서번호", "Source / document identifier"), current.get("source", ""))
        product = st.text_input(bi("적용 제품", "Applicable product"), current.get("product", ""))
        batch = st.text_input(bi("적용 배치 (비배치 자료는 범위 명시)", "Applicable batch (state scope for non-batch documents)"), current.get("batch", ""))
        stage = st.text_input(bi("적용 단계", "Applicable lifecycle stage"), current.get("stage", ""))
        effective = st.date_input(bi("시행일", "Effective date"), value=date.fromisoformat(current["effective_date"]) if current.get("effective_date") else None)
        reviewer = st.text_input(bi("확인한 검토자", "Reviewer"), current.get("reviewer", ""))
        status = st.selectbox(bi("적용 근거 확인 상태", "Applicability confirmation"), ["unconfirmed", "confirmed", "conflicting"],
                              index=["unconfirmed", "confirmed", "conflicting"].index(current.get("status", "unconfirmed")))
        submitted = st.form_submit_button(bi("문서 출처·범위 저장", "Save document source and scope"))
    if submitted:
        try:
            st.session_state[STATE_KEY] = save_document(trace, file_id, dict(version=version, system=system, source=source, product=product, batch=batch,
                stage=stage, effective_date=effective.isoformat() if effective else "", reviewer=reviewer, status=status))
            st.rerun()
        except ValueError as exc:
            st.error(str(exc))
    scope = applicability(current, profile.get("product", ""), profile.get("batch", ""), profile.get("stage", ""))
    st.write(bi("현재 제품·배치·단계와의 대조", "Match to current product, batch and stage") + ": " + scope)
    st.caption(bi("현재 배치가 비어 있으면 적용 범위는 미확인입니다. 버전 문자열은 자동으로 최신 순서를 판정하지 않습니다.",
                  "An empty current batch leaves scope unconfirmed. Version labels are not automatically ordered by recency."))
    if len(files) >= 2:
        st.markdown("#### " + bi("두 문서의 텍스트 변경 비교", "Compare text changes between two documents"))
        other = st.selectbox(bi("이전 / 비교 기준 문서", "Earlier / reference document"), [key for key in files if key != file_id],
                             format_func=lambda key: files[key]["name"], key="trace_old_file")
        st.caption(bi("현재 선택 문서를 이후 버전으로 비교합니다. 변경 영향과 승인 여부는 검토자가 확인해야 합니다.",
                      "Compare the selected document as the later version. A reviewer must assess change impact and approval."))
        if st.button(bi("버전 변경 비교", "Compare versions"), key="trace_compare"):
            cache = st.session_state.setdefault("customer_document_insights", {})
            for key in (other, file_id):
                if key not in cache:
                    cache[key] = extract_document(files[key]["name"], files[key]["content"])
            try:
                st.session_state["trace_diff"] = {"old_id": other, "new_id": file_id, **compare_documents(cache[other], cache[file_id])}
            except ValueError as exc:
                st.session_state.pop("trace_diff", None)
                st.error(str(exc))
        diff = st.session_state.get("trace_diff", {})
        if diff.get("old_id") == other and diff.get("new_id") == file_id:
            st.metric(bi("변경 구간", "Changed text blocks"), len(diff["changes"]))
            if diff["partial"]:
                st.warning(bi("추출 범위 일부의 비교입니다. 문서 전체 비교가 아닙니다.", "Partial extraction comparison; this does not compare entire documents."))
            if not diff["changes"]:
                st.info(bi("추출한 텍스트에서 변경을 찾지 못했습니다. 서식·그림·미추출 영역은 확인 대상입니다.",
                           "No changes found in extracted text. Check formatting, images and unextracted content separately."))
            for index, change in enumerate(diff["changes"][:50], 1):
                with st.expander(f"{index}. {change['change']}"):
                    left, right = st.columns(2)
                    left.caption(files[other]["name"])
                    right.caption(files[file_id]["name"])
                    for column, side in ((left, "old"), (right, "new")):
                        column.code("\n".join(f"[{line['location']} · {source_label(line['source_ref'])}] {line['text']}" for line in change[side]), language=None)
                    if change["truncated"]:
                        st.caption(bi("표시를 구간당 20줄로 제한했습니다.", "Display limited to 20 lines per block."))
            if len(diff["changes"]) > 50:
                st.caption(bi("화면에는 첫 50구간을 표시합니다. 전체 결과를 내려받으세요.", "First 50 blocks shown. Download the complete results."))
            st.download_button(bi("변경 비교 결과 (JSON)", "Download comparison (JSON)"), json.dumps(diff, ensure_ascii=False, indent=2),
                               file_name="VCC_version_diff.json", mime="application/json", key="trace_diff_download")
    st.markdown("#### " + bi("저장한 출처 근거·검토 조치", "Saved source evidence and review actions"))
    for evidence in trace["evidence"]:
        with st.expander(f"{files[evidence['file_id']]['name']} · {evidence['location']} · {evidence['status']}"):
            st.caption(bi("근거 기록 당시 버전", "Version when recorded") + ": " + evidence["document_snapshot"].get("version", ""))
            st.caption(source_label(evidence["source_ref"]))
            st.code(evidence["excerpt"], language=None)
            for label, field in [(bi("확인값·해석", "Checked value"), "confirmed_value"),
                                 (bi("변경 영향", "Change impact"), "impact"), ("CTD", "ctd_target"),
                                 (bi("추가자료", "Information needed"), "request"),
                                 (bi("담당자", "Owner"), "owner"), (bi("기한", "Due date"), "due_date")]:
                if evidence[field]:
                    st.write(label + ": " + evidence[field])
            if evidence.get("invalidation"):
                st.warning(evidence["invalidation"])
    st.download_button(bi("문서 추적 기록 (JSON)", "Download document trace (JSON)"), json.dumps(trace, ensure_ascii=False, indent=2),
                       file_name="VCC_document_trace.json", mime="application/json", key="trace_download")


def render_evidence_capture(state, file_id, topic, lang):
    def bi(ko, en):
        return ko if lang == "ko" else en
    evidence = topic.get("evidence", [])
    if not evidence:
        return
    trace = get_trace(state["files"])
    with st.expander(bi("이 원문 근거를 검토 기록에 연결", "Link source evidence to a review record")):
        index = st.selectbox(bi("기록할 원문 위치", "Source location to record"), list(range(len(evidence))),
                             format_func=lambda i: evidence[i]["location"], key="trace_capture_location")
        candidate = {**evidence[index], "topic": topic["key"]}
        previous = next((item for item in trace["evidence"] if item["file_id"] == file_id and item["topic"] == topic["key"] and item["location"] == candidate["location"]), {})
        with st.form(f"trace_evidence_{file_id}_{topic['key']}_{index}_{lang}"):
            value = st.text_input(bi("검토한 값·해석", "Checked value / interpretation"), previous.get("confirmed_value", ""))
            reviewer = st.text_input(bi("검토자", "Reviewer"), previous.get("reviewer", ""))
            status = st.selectbox(bi("근거 확인 상태", "Evidence confirmation"), ["unconfirmed", "confirmed", "conflicting"],
                                  index=["unconfirmed", "confirmed", "conflicting"].index(previous.get("status", "unconfirmed")))
            ctd_target = st.text_input(bi("CTD 수정 위치", "CTD action location"), previous.get("ctd_target", ""))
            impact = st.text_area(bi("변경 영향·검토 주석", "Change impact / review notes"), previous.get("impact", ""))
            request = st.text_area(bi("필요한 추가자료", "Additional information needed"), previous.get("request", ""))
            owner = st.text_input(bi("담당자", "Owner"), previous.get("owner", ""))
            due = st.date_input(bi("기한", "Due date"), value=date.fromisoformat(previous["due_date"]) if previous.get("due_date") else None)
            submitted = st.form_submit_button(bi("출처 연결 검토 기록 저장", "Save source-linked review record"))
        if submitted:
            try:
                st.session_state[STATE_KEY] = save_evidence(trace, file_id, candidate, dict(confirmed_value=value, reviewer=reviewer, status=status,
                    ctd_target=ctd_target, impact=impact, request=request, owner=owner, due_date=due.isoformat() if due else ""))
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))

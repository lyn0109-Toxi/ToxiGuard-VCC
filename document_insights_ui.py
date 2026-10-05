"""Session-only visual map of automatically extracted CTD evidence."""
import json

import pandas as pd
import streamlit as st

from document_insights import extract_document

CACHE_KEY = "customer_document_insights"


def render_insights(state: dict, lang: str) -> None:
    def bi(ko, en):
        return ko if lang == "ko" else en

    st.subheader(bi("문서에서 추출한 검토 지도", "Document review map"))
    st.caption(bi("업로드한 원문에서 찾은 후보입니다. 항목을 선택해 근거를 확인하세요. 검토 완료나 적합 판정은 아닙니다.",
                  "Candidates found in your uploaded source. Select a topic to inspect its evidence. These are not completed reviews or compliance findings."))
    # No shared cache: derived document content stays with the file's session.
    cache = st.session_state.setdefault(CACHE_KEY, {})
    for key in list(cache):
        if key not in state["files"]:
            del cache[key]
    if not state["files"]:
        st.info(bi("‘섹션별 파일 접수’에서 CTD 파일을 등록하면 분석 결과가 표시됩니다.",
                   "Register a CTD file in Files by section to see its analysis."))
        return
    file_id = st.selectbox(bi("분석할 문서", "Document to analyse"), list(state["files"]),
                          format_func=lambda key: state["files"][key]["name"], key="doc_insights_file")
    item = state["files"][file_id]
    if file_id not in cache:
        with st.spinner(bi("문서의 텍스트와 검토 항목을 추출하고 있습니다…", "Extracting text and review topics…")):
            cache[file_id] = extract_document(item["name"], item["content"])
    result = cache[file_id]
    statuses = {
        "unsupported": ("자동 추출은 PDF·DOCX·XLSX·TXT를 지원합니다. 이 형식은 원본을 확인하거나 지원 형식으로 변환해 등록하세요.", "Automatic extraction supports PDF, DOCX, XLSX and TXT. Inspect this original or convert it to a supported format."),
        "encrypted": ("암호화된 PDF는 추출할 수 없습니다. 암호화되지 않은 사본을 등록하세요.", "Encrypted PDFs cannot be extracted. Register an unencrypted copy."),
        "empty": ("추출 가능한 텍스트가 없습니다. 스캔 PDF는 OCR로 텍스트를 추가한 뒤 등록하세요.", "No extractable text found. For a scanned PDF, add text using OCR before registering it."),
        "limit": ("문서가 자동 추출 처리 한도를 초과했습니다. 필요한 부분을 나눠 등록하세요.", "The document exceeds extraction limits. Register the relevant parts separately."),
        "timeout": ("추출 시간 한도를 초과했습니다. 필요한 부분을 나눠 등록하거나 원본을 확인하세요.", "Extraction timed out. Register smaller parts or inspect the original."),
        "error": ("이 문서의 텍스트를 읽을 수 없습니다. 손상 여부를 확인하거나 지원 형식으로 다시 저장하세요.", "Could not read this document. Check for damage or resave in a supported format."),
    }
    if result["status"] != "ok":
        st.warning(bi(*statuses.get(result["status"], statuses["error"])))
        return
    if result["truncated"]:
        st.warning(bi("일부만 분석했습니다: 최대 PDF 120쪽, 텍스트 30만 자 또는 2,000개 텍스트 블록. 나머지는 별도로 확인하세요.",
                      "Partial analysis: at most 120 PDF pages, 300,000 characters or 2,000 text blocks. Inspect the remaining content separately."))
    st.caption(bi("분석은 서버 내부에서 수행합니다. 문서를 외부 AI 서비스에 전송하지 않습니다. 등록한 섹션과 원문에서 탐지한 섹션은 별개입니다.",
                  "Analysis runs locally on the server without sending documents to an external AI service. Registered sections and sections detected in the text are separate."))
    if item["extension"] == "xlsx":
        st.caption(bi("Excel은 저장된 셀 값을 읽으며 수식을 재계산하지 않습니다. 수식과 캐시 값의 최신성은 원본에서 확인하세요.",
                      "Excel uses stored cell values without recalculating formulas. Check formulas and the freshness of cached values in the original workbook."))
    columns = st.columns(3)
    columns[0].metric(bi("약물명 후보", "Drug name candidates"), len(result["drugs"]))
    columns[1].metric(bi("탐지된 CTD 섹션", "Detected CTD sections"), len(result["sections"]))
    columns[2].metric(bi("근거가 있는 검토 주제", "Topics with evidence"), sum(topic["matches"] > 0 for topic in result["topics"]))
    st.markdown("#### " + bi("약물명·제품명 후보", "Drug / product name candidates"))
    if result["drugs"]:
        for drug in result["drugs"]:
            st.code(f"{drug['name']}\n{drug['location']} · {drug['excerpt']}", language=None)
    else:
        st.info(bi("약물명 후보를 찾지 못했습니다. 원문의 ‘제품명’, ‘주성분’, ‘Drug substance:’ 등 명칭 표기를 직접 확인하세요.",
                   "No drug name candidate found. Check the original name fields such as Product name or Drug substance."))
    if result["sections"]:
        with st.expander(bi("원문에서 탐지한 CTD 섹션", "CTD sections detected in source")):
            for section in result["sections"]:
                st.code(f"{section['section']} · {section['location']}\n{section['excerpt']}", language=None)
    label = "ko" if lang == "ko" else "en"
    frame = pd.DataFrame({bi("검토 주제", "Review topic"): [t[label] for t in result["topics"]],
                          bi("근거 블록 수", "Evidence blocks"): [t["matches"] for t in result["topics"]]})
    st.bar_chart(frame.set_index(frame.columns[0]), horizontal=True)
    st.caption(bi("막대는 키워드가 발견된 텍스트 블록 수이며, 자료의 충분성·품질·적합성을 뜻하지 않습니다. 0은 분석 범위에서 찾지 못했다는 뜻입니다.",
                  "Bars count text blocks containing topic keywords, not evidence sufficiency, quality or compliance. Zero means not found within the analysed text."))
    topic_key = st.selectbox(bi("원문 근거를 확인할 검토 주제", "Review topic to inspect"),
                            [t["key"] for t in result["topics"]],
                            format_func=lambda key: next(t[label] for t in result["topics"] if t["key"] == key),
                            key="doc_insights_topic")
    topic = next(t for t in result["topics"] if t["key"] == topic_key)
    st.write(topic["review_ko" if lang == "ko" else "review_en"])
    if not topic["evidence"]:
        st.info(bi("이 주제의 키워드를 찾지 못했습니다. 누락으로 단정하지 말고 원문과 다른 문서를 확인하세요.",
                   "No keywords found for this topic. Check the source and other documents before concluding it is missing."))
    for evidence in topic["evidence"]:
        st.caption(evidence["location"])
        st.code(evidence["excerpt"], language=None)
        if evidence.get("source_ref"):
            from document_trace import source_label
            st.caption(source_label(evidence["source_ref"]))
    from document_trace_ui import render_evidence_capture
    render_evidence_capture(state, file_id, topic, lang)
    st.download_button(bi("추출 결과 내려받기 (JSON)", "Download extracted results (JSON)"),
                       json.dumps({"file_name": item["name"], **result}, ensure_ascii=False, indent=2),
                       file_name="VCC_document_insights.json", mime="application/json", key="doc_insights_download")
    with st.expander(bi("추출된 전체 텍스트 확인", "Inspect extracted text")):
        st.code("\n\n".join(f"[{u['location']}]\n{u['text']}" for u in result["units"]), language=None)

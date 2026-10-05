"""Reviewer-confirmed dosage-form scope, separate from example evidence tables."""
from __future__ import annotations

import copy
from datetime import date
import hashlib
from html import escape
import json
import re
from typing import Any

import pandas as pd
import streamlit as st


STATE_KEY = "dosage_review_checklists"
STATUSES = ("unconfirmed", "reviewed", "not_applicable")
CONTEXT_FIELDS = ("product", "active_substance", "dosage", "route", "strength", "batch",
                  "clinical_material", "api_supplier", "formulation_platform", "stage")
TEMPLATES = {
    "": ("검토 범위를 선택하세요", "Choose review scope"),
    "oral_nonsterile": ("경구 비무균 제제", "Oral, nonsterile product"),
    "sterile": ("주사제 / 무균 제제", "Injectable / sterile product"),
    "other": ("기타 제형 / 적용 범위 추가 확인", "Other form / additional scope review"),
}

# These are review prompts, not regulatory acceptance criteria or exhaustive requirements.
COMMON_ITEMS = (
    ("product_context", "3.2.S.1 / 3.2.P.1", "제품·원료·함량·적용 배치 연결", "Product, API, strength and applicable batch linkage"),
    ("document_versions", "3.2.S.4 / 3.2.P.5", "LIMS·QC 시험법·허가 문서의 버전 및 적용 시점", "LIMS, QC method and submission versions and effective dates"),
    ("concentration_basis", "3.2.S.4.3 / 3.2.P.5.3", "농도·단위·희석 단계·순도/수분/역가 보정 근거", "Concentration, units, dilution steps and purity/water/potency correction basis"),
    ("analytical_evidence", "3.2.S.4 / 3.2.P.5", "규격·함량·불순물 및 시험법 밸리데이션 근거", "Specification, assay, impurities and analytical validation evidence"),
    ("supplier_changes", "3.2.S.2 / 3.2.S.4 / 3.2.P.2", "공급처·DMF 변경 내용과 제품 영향", "Supplier/DMF changes and product impact"),
    ("stability_packaging", "3.2.S.7 / 3.2.P.7 / 3.2.P.8", "안정성·보관·포장 및 적용 배치", "Stability, storage, packaging and applicable batches"),
)
FORM_ITEMS = {
    "oral_nonsterile": (
        ("oral_release", "3.2.P.2 / 3.2.P.5", "제형에 따른 용출·붕해·방출 시험 적용성", "Applicability of dissolution, disintegration or release testing"),
        ("oral_uniformity", "3.2.P.3 / 3.2.P.5", "함량 균일성·혼합/공정 관리 적용성", "Applicability of dosage uniformity and blend/process controls"),
        ("oral_microbiology", "3.2.P.5", "비무균 미생물 한도·보존제 관리 적용성", "Applicability of nonsterile microbial limits and preservative controls"),
    ),
    "sterile": (
        ("sterility_assurance", "3.2.P.3 / 3.2.P.5", "무균보증·멸균/무균공정 및 검증 근거", "Sterility assurance, sterilization/aseptic processing and validation"),
        ("endotoxin", "3.2.P.5", "엔도톡신/발열성 시험 및 제품별 허용기준 근거", "Endotoxin/pyrogen testing and product-specific limit rationale"),
        ("container_integrity", "3.2.P.7 / 3.2.P.8", "용기 밀봉 무결성 및 안정성 기간 근거", "Container closure integrity across shelf life"),
        ("injectable_performance", "3.2.P.2 / 3.2.P.5", "입자·재구성·주사성·방출 시험의 제품별 적용성", "Product-specific applicability of particles, reconstitution, syringeability and release tests"),
    ),
    "other": (
        ("form_specific_scope", "3.2.P.2 / 3.2.P.5", "제형·투여경로별 추가 품질항목 및 적용 범위 확인", "Confirm additional quality attributes for the dosage form and route"),
    ),
}


def bi(lang: str, ko: str, en: str) -> str:
    return ko if lang == "ko" else en


def profile_key(profile: dict[str, Any]) -> str:
    context = {field: str(profile.get(field, "")) for field in CONTEXT_FIELDS}
    return hashlib.sha256(json.dumps(context, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:20]


def suggest_template(profile: dict[str, Any]) -> str:
    """Suggest scope only; route/form strings never confirm applicability."""
    text = " ".join(str(profile.get(field, "")) for field in ("dosage", "route")).lower()
    oral = bool(re.search(r"\b(?:oral|tablet|capsule|per\s+os)\b|경구|정제|캡슐", text))
    sterile_text = re.sub(r"\bnon[\s-]?sterile\b|비무균", "", text)
    sterile = bool(re.search(r"\b(?:injection|injectable|sterile|intramuscular|intravenous|subcutaneous|parenteral)\b|주사|무균", sterile_text))
    if sterile and oral:
        return ""
    if sterile:
        return "sterile"
    if oral:
        return "oral_nonsterile"
    return ""


def new_state(profile: dict[str, Any]) -> dict[str, Any]:
    return {"profile_key": profile_key(profile),
            "context": {field: str(profile.get(field, "")) for field in CONTEXT_FIELDS},
            "template": suggest_template(profile), "confirmed": False, "records": {}}


def scope_items(template: str) -> tuple:
    if template not in TEMPLATES:
        raise ValueError("Unknown checklist template")
    return COMMON_ITEMS + FORM_ITEMS.get(template, ())


def configure_scope(state: dict, template: str, confirmed: bool = False) -> dict:
    if template not in TEMPLATES:
        raise ValueError("Unknown checklist template")
    if confirmed and not template:
        raise ValueError("Choose a dosage-form scope before confirming it")
    updated = copy.deepcopy(state)
    updated.update(template=template, confirmed=bool(confirmed))
    return updated


def update_item(state: dict, item_id: str, status: str = "unconfirmed", *,
                note: str = "", source: str = "", reason: str = "", owner: str = "",
                due_date: str | date | None = None) -> dict:
    """Save an explicit reviewer action; no evidence or validation table is touched."""
    if not state.get("confirmed") or not state.get("template"):
        raise ValueError("Confirm the dosage-form scope first")
    if item_id not in {item[0] for item in scope_items(state["template"])}:
        raise ValueError("The item is outside the selected dosage-form scope")
    if status not in STATUSES:
        raise ValueError("Unknown checklist status")
    if status == "not_applicable" and not reason.strip():
        raise ValueError("A reason is required for Not applicable")
    if status == "reviewed" and (not source.strip() or not note.strip()):
        raise ValueError("A source reference and review note are required for Reviewed")
    due = due_date.isoformat() if isinstance(due_date, date) else str(due_date or "").strip()
    if due:
        due = date.fromisoformat(due).isoformat()
    updated = copy.deepcopy(state)
    updated["records"][item_id] = {"status": status, "note": note.strip(), "source": source.strip(),
                                  "reason": reason.strip(), "owner": owner.strip(), "due_date": due}
    return updated


def status_label(status: str, lang: str) -> str:
    return {"unconfirmed": bi(lang, "미확인", "Unconfirmed"),
            "reviewed": bi(lang, "검토 기록됨", "Review recorded"),
            "not_applicable": bi(lang, "해당없음", "Not applicable")}[status]


def item_rows(state: dict, lang: str = "en") -> list[dict]:
    rows = []
    for item_id, ctd, ko, en in scope_items(state["template"]):
        record = state["records"].get(item_id, {})
        rows.append({"id": item_id, "item": bi(lang, ko, en), "ctd": ctd,
                     "status": record.get("status", "unconfirmed"),
                     **{key: record.get(key, "") for key in ("source", "note", "reason", "owner", "due_date")}})
    return rows


def display_frame(state: dict, lang: str) -> pd.DataFrame:
    return pd.DataFrame([{bi(lang, "검토 항목", "Review item"): row["item"],
                          "CTD": row["ctd"], bi(lang, "상태", "State"): status_label(row["status"], lang),
                          bi(lang, "출처", "Source reference"): row["source"],
                          bi(lang, "검토 메모", "Review note"): row["note"],
                          bi(lang, "해당없음 사유", "Not applicable reason"): row["reason"],
                          bi(lang, "담당자", "Owner"): row["owner"],
                          bi(lang, "기한", "Due date"): row["due_date"]}
                         for row in item_rows(state, lang)])


def checklist_report(profile: dict[str, Any], lang: str = "en", state: dict | None = None) -> str:
    """Export current-profile records; hidden records from other scopes stay excluded."""
    if state is None:
        state = st.session_state.get(STATE_KEY, {}).get(profile_key(profile))
    title = bi(lang, "제형별 검토 체크리스트", "Dosage-form review checklist")
    disclaimer = bi(lang, "검토자 기록이며 규제 적합성 또는 검토 완료의 자동 판정이 아닙니다. 제형·투여경로 문자열만으로 적용 범위를 확정하지 않습니다.",
                    "Reviewer records, not an automated compliance or review-completion decision. Form and route text alone do not confirm applicability.")
    output = f"## {title}\n\n{disclaimer}\n\n"
    if state is None:
        return output + bi(lang, "현재 제품의 체크리스트가 아직 설정되지 않았습니다.\n", "The checklist has not been configured for the current product.\n")
    if state["profile_key"] != profile_key(profile):
        raise ValueError("Checklist context does not match the current product profile")
    clean = lambda value: escape(str(value), quote=False).replace("|", "\\|").replace("\r", " ").replace("\n", "<br>")
    template = TEMPLATES[state["template"]][0 if lang == "ko" else 1]
    confirmation = bi(lang, "검토자 확인", "Reviewer confirmed") if state["confirmed"] else bi(lang, "범위 미확인", "Scope unconfirmed")
    context_labels = (("product", bi(lang, "제품", "Product")), ("dosage", bi(lang, "제형", "Dosage form")),
                      ("route", bi(lang, "투여경로", "Route")), ("strength", bi(lang, "함량", "Strength")),
                      ("batch", bi(lang, "검토 대상 배치", "Review batch")),
                      ("clinical_material", bi(lang, "임상 배치", "Clinical batches")))
    output += "\n".join(f"{label}: {clean(state['context'][field])}  " for field, label in context_labels)
    output += f"\n\n{clean(template)} · {confirmation}\n\n"
    frame = display_frame(state, lang)
    output += "| " + " | ".join(map(clean, frame.columns)) + " |\n"
    output += "| " + " | ".join("---" for _ in frame.columns) + " |\n"
    output += "\n".join("| " + " | ".join(map(clean, row)) + " |" for row in frame.itertuples(index=False, name=None)) + "\n"
    if not state["confirmed"]:
        output += "\n" + bi(lang, "범위 확인 전 항목은 초안입니다.\n", "Items remain a draft until the scope is confirmed.\n")
    return output


def render_checklist(lang: str, profile: dict[str, Any]) -> None:
    context_key = profile_key(profile)
    registry = st.session_state.setdefault(STATE_KEY, {})
    state = registry.setdefault(context_key, new_state(profile))
    prefix = "dosage_check_" + context_key
    st.subheader(bi(lang, "제형별 검토 체크리스트", "Dosage-form review checklist"))
    st.caption(bi(lang,
        "제품 프로필에 맞는 검토 범위를 검토자가 확인하세요. 미확인부터 시작하며 기존 예시 근거표와 별도로 저장합니다. ‘검토 기록됨’은 적합성 또는 최종 승인 판정이 아닙니다.",
        "Confirm the review scope for this product. Items start Unconfirmed and are saved separately from example evidence tables. Review recorded does not mean compliance or final approval."))
    st.caption(bi(lang, "제형·투여경로는 범위 제안에만 사용됩니다. 경구 비무균 템플릿은 무균·엔도톡신·밀봉 무결성 요청을 기본 포함하지 않습니다.",
        "Form and route are used only to suggest a scope. The oral nonsterile template excludes sterility, endotoxin and container integrity requests by default."))
    if state.pop("saved_notice", False):
        st.success(bi(lang, "검토 기록을 저장했습니다.", "Review record saved."))
    with st.form(prefix + "_scope_form"):
        selected = st.selectbox(bi(lang, "적용 제형 템플릿", "Dosage-form template"), list(TEMPLATES),
                                index=list(TEMPLATES).index(state["template"]),
                                format_func=lambda key: TEMPLATES[key][0 if lang == "ko" else 1], key=prefix + "_scope")
        confirmed = st.checkbox(bi(lang, "이 제품·배치의 적용 범위를 검토자로서 확인했습니다", "I confirm the applicable scope for this product and its batches"),
                                value=state["confirmed"], key=prefix + "_confirmed")
        if st.form_submit_button(bi(lang, "검토 범위 저장", "Save review scope")):
            try:
                state = configure_scope(state, selected, confirmed)
                registry[context_key] = state
            except ValueError as error:
                st.error(str(error))
    if not state["template"]:
        st.info(bi(lang, "제형이 불명확합니다. 검토 범위를 직접 선택하고 확인하세요.",
                   "The dosage form is unclear. Choose and confirm a review scope."))
        return
    if state["template"] == "other":
        st.info(bi(lang, "공통 항목만 포함됩니다. 제형별 추가 품질항목을 별도로 확인해야 합니다.",
                   "Only common prompts are included. Additional quality attributes for this dosage form still need review."))
    rows = item_rows(state, lang)
    counts = st.columns(3)
    for column, status in zip(counts, STATUSES):
        column.metric(status_label(status, lang), sum(row["status"] == status for row in rows))
    st.dataframe(display_frame(state, lang), width="stretch", hide_index=True)
    if not state["confirmed"]:
        st.info(bi(lang, "범위를 확인한 뒤 검토 상태를 기록할 수 있습니다.", "Confirm the scope before recording item review states."))
    else:
        labels = {row["id"]: row["item"] for row in rows}
        item_id = st.selectbox(bi(lang, "기록할 검토 항목", "Review item to record"), list(labels),
                               format_func=labels.__getitem__, key=prefix + "_item_" + state["template"])
        record = state["records"].get(item_id, {})
        form_key = prefix + "_" + item_id
        with st.form(form_key + "_record"):
            status = st.selectbox(bi(lang, "검토 상태", "Review state"), list(STATUSES),
                                  index=STATUSES.index(record.get("status", "unconfirmed")),
                                  format_func=lambda value: status_label(value, lang), key=form_key + "_status")
            source = st.text_input(bi(lang, "출처 (문서·버전·페이지·표·셀)", "Source reference (document, version, page, table, cell)"),
                                   value=record.get("source", ""), key=form_key + "_source", max_chars=4000)
            note = st.text_area(bi(lang, "검토 메모 / 필요한 추가자료", "Review note / additional information needed"),
                                value=record.get("note", ""), key=form_key + "_note", max_chars=8000)
            reason = st.text_area(bi(lang, "해당없음 사유 (해당없음 선택 시 필수)", "Reason (required for Not applicable)"),
                                  value=record.get("reason", ""), key=form_key + "_reason", max_chars=4000)
            owner = st.text_input(bi(lang, "담당자", "Owner"), value=record.get("owner", ""), key=form_key + "_owner", max_chars=500)
            due = st.date_input(bi(lang, "기한 (선택)", "Due date (optional)"),
                                value=date.fromisoformat(record["due_date"]) if record.get("due_date") else None,
                                key=form_key + "_due")
            if st.form_submit_button(bi(lang, "항목 기록 저장", "Save item record")):
                try:
                    updated = update_item(state, item_id, status, note=note, source=source,
                                          reason=reason, owner=owner, due_date=due)
                    updated["saved_notice"] = True
                    registry[context_key] = updated
                    st.rerun()
                except ValueError as error:
                    st.error(str(error))
    st.download_button(bi(lang, "체크리스트 내려받기", "Download checklist"), checklist_report(profile, lang, state),
                       file_name="dosage-review-checklist.md", mime="text/markdown", key=prefix + "_download")

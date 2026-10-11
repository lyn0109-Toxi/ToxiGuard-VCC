"""Korean / English analytical-method workspace for the existing Streamlit app."""
from __future__ import annotations

from copy import deepcopy
from html import escape
import json
from typing import Any

import pandas as pd
import streamlit as st
from analytical_visuals import UI_BUILD, STYLE, flow_html, missing_preparation, section_html, status_html

from analytical_workspace import (
    BUILD, CATALOG, LABELS, MASS_MG, VOLUME_ML, add_custom_test, calculate_preparation,
    comparison_rows, daily_amounts, demo_workspace, export_workbook, impurity_limit,
    label, new_workspace, record_review, refresh_reviews, report_markdown, select_tests, test_label,
)

STATE_KEY = "analytical_method_workspace"

def state() -> dict[str, Any]:
    st.session_state.setdefault(STATE_KEY, new_workspace())
    result = st.session_state[STATE_KEY]
    # Batch/stage changes from another page invalidate reviews before memo/export.
    refresh_reviews(result, dict(st.session_state.get("profile_values", {})))
    return result

def _object(path: tuple[str, ...]) -> dict[str, Any]:
    result = state()
    for part in path:
        result = result[part]
    return result

def _save(path: tuple[str, ...], field: str, key: str) -> None:
    _object(path)[field] = st.session_state[key]
    refresh_reviews(state())

def _key(path: tuple[str, ...], field: str) -> str:
    return "am_" + "_".join((*path, field))

def _input(path: tuple[str, ...], field: str, lang: str, options: list[str] | None = None, number: bool = False, area: bool = False) -> Any:
    record = _object(path)
    key = _key(path, field)
    st.session_state[key] = record.get(field)
    args = {"key": key, "on_change": _save, "args": (path, field, key)}
    if options is not None:
        display = (lambda v: test_label(v, state(), lang)) if field in {"active_method_test", "active_calculation_test"} else (lambda v: label(v, lang))
        return st.selectbox(label(field, lang), options, format_func=display, **args)
    if number:
        return st.number_input(label(field, lang), min_value=0.0, value=None, format="%.6f", **args)
    if area:
        return st.text_area(label(field, lang), **args)
    return st.text_input(label(field, lang), **args)

def _demo() -> None:
    st.session_state[STATE_KEY] = demo_workspace()
    # Data editors hold frontend deltas; remove them when an explicit demo replaces this workspace.
    for key in list(st.session_state):
        if key.startswith("am_"):
            del st.session_state[key]

def _select() -> None:
    select_tests(state(), st.session_state.am_selected)

def _add_test() -> None:
    try:
        add_custom_test(state(), st.session_state.am_custom_name)
        st.session_state.am_custom_error = ""
    except ValueError as exc:
        st.session_state.am_custom_error = str(exc)

def _provenance(record: dict[str, Any], fields: list[str], key: str, lang: str, stored_field: str) -> None:
    with st.expander("값별 입력 / 출처 / 기준" if lang == "ko" else "Per-value inputs / sources / basis"):
        st.caption("항목 하나씩 출처를 편집합니다. 다른 항목의 기록은 유지됩니다." if lang == "ko" else "Edit one field's source at a time. Other field records are retained.")
        selected = st.selectbox("출처를 기록할 입력 항목" if lang == "ko" else "Input field to document", fields, format_func=lambda f: label(f, lang), key=key + "_field")
        saved = next((row for row in record.get(stored_field, []) if row["field"] == selected), {})
        kinds = ["entered", "source_derived", "proposal", "example"]
        for field in ("value_kind", "source", "version", "location", "basis_note"):
            widget_key = key + "_" + selected + "_" + field
            st.session_state[widget_key] = saved.get(field, "entered" if field == "value_kind" else "")
            args = dict(key=widget_key, on_change=_origin_save, args=(record, stored_field, selected, field, widget_key))
            if field == "value_kind":
                st.selectbox(label(field, lang), kinds, format_func=lambda v: label(v, lang), **args)
            else:
                st.text_input(label(field, lang), **args)
        with st.expander("기록된 출처 전체 보기" if lang == "ko" else "View all recorded sources"):
            rows = record.get(stored_field, [])
            if rows:
                frame = pd.DataFrame(rows).fillna("")
                for field in ("field", "value_kind"):
                    frame[field] = frame[field].map(lambda v: label(v, lang))
                st.dataframe(frame.rename(columns={f: label(f, lang) for f in frame.columns}), hide_index=True, width="stretch")
            else:
                st.caption("출처 미기록" if lang == "ko" else "No sources recorded")

def _origin_save(record: dict[str, Any], stored_field: str, selected: str, field: str, widget_key: str) -> None:
    rows = record.setdefault(stored_field, [])
    row = next((row for row in rows if row["field"] == selected), None)
    if row is None:
        row = {"field": selected, "value_kind": "entered", "source": "", "version": "", "location": "", "basis_note": ""}
        rows.append(row)
    row[field] = st.session_state[widget_key]
    refresh_reviews(state())

def _section(number: str, en: str, ko: str, lang: str, detail_en: str = "", detail_ko: str = "") -> None:
    st.markdown(section_html(number, ko if lang == "ko" else en, detail_ko if lang == "ko" else detail_en), unsafe_allow_html=True)

def _gap(text: str) -> None:
    st.markdown('<div class="am-missing">' + escape(text) + '</div>', unsafe_allow_html=True)

FAMILIES = [
    ("core", "Identity & content", "동일성·함량", ["identity", "assay", "appearance"]),
    ("impurities", "Impurities & exposure", "불순물·노출", ["related_substances", "residual_solvents", "elemental_impurities", "mutagenic_impurities", "nitrosamines"]),
    ("performance", "Dosage-form performance", "제형 성능", ["dissolution", "disintegration", "uniformity"]),
    ("physical", "Physical properties", "물리적 특성", ["water", "particle_size", "solid_form"]),
    ("micro", "Microbiological quality", "미생물학적 품질", ["microbiology", "sterility", "endotoxin"]),
    ("other", "Other & custom tests", "기타·사용자 시험", ["other"]),
]

def _select_family(keys: list[str], widget_key: str) -> None:
    chosen = st.session_state[widget_key]
    selected = [key for key in state()["selected"] if key not in keys]
    select_tests(state(), selected + [key for key in keys if key in chosen])

def _step_widget_key(key: str, kind: str, lang: str) -> str:
    base = "am_steps_" + key + "_" + kind + "_" + lang
    revision = st.session_state.get("am_steps_revision_" + key + "_" + kind, 0)
    return base + (f"_v{revision}" if revision else "")

def _replace_steps(key: str, kind: str, steps: list[dict[str, Any]]) -> None:
    prep = state()["tests"][key][kind]
    prep["steps"] = steps
    revision_key = "am_steps_revision_" + key + "_" + kind
    st.session_state[revision_key] = st.session_state.get(revision_key, 0) + 1
    refresh_reviews(state())

def _step_change(key: str, kind: str, widget_key: str, baseline: list[dict[str, Any]], lang: str) -> None:
    """Reconcile editor deltas before any method/calculate review status renders."""
    delta = st.session_state[widget_key]
    rows = deepcopy(baseline)
    reverse = {label(field, lang): field for field in ("aliquot_ml", "final_ml")}
    for index, changes in delta.get("edited_rows", {}).items():
        for column, value in changes.items():
            rows[int(index)][reverse[column]] = value
    deleted = set(delta.get("deleted_rows", []))
    rows = [row for index, row in enumerate(rows) if index not in deleted]
    rows += [{field: row.get(label(field, lang)) for field in ("aliquot_ml", "final_ml")} for row in delta.get("added_rows", [])]
    _replace_steps(key, kind, rows)

def _review(key: str, kind: str, lang: str) -> None:
    record = state()["tests"][key]
    review = record[kind].get("review") if kind in {"sample", "reference"} else record.get(kind + "_review")
    st.caption(label("reviewed" if review else "pending", lang))
    if review:
        st.write(f"{label('reviewer', lang)}: {review['reviewer']} · {review['at']}")
        st.write(review["note"])
    prefix = "am_review_" + key + "_" + kind
    reviewer = st.text_input(label("reviewer", lang), key=prefix + "_reviewer")
    note = st.text_input(label("review_note", lang), key=prefix + "_note")
    names = {"sample": ("Record sample calculation review", "검액 계산 검토 기록"), "reference": ("Record reference calculation review", "표준액 계산 검토 기록"), "evidence": ("Record source / applicability review", "원문 / 적용성 검토 기록"), "experiment": ("Record experimental-support review", "실험 근거 검토 기록")}
    if st.button(names[kind][lang == "ko"], key=prefix + "_button"):
        try:
            record_review(state(), key, kind, reviewer, note)
            st.rerun()
        except (ValueError, TypeError, OverflowError) as exc:
            st.warning(("검토 기록에 필요한 입력: " if lang == "ko" else "Review needs: ") + ", ".join(label(v.strip(), lang) for v in str(exc).split(",")))

def _product(lang: str) -> None:
    s = state()
    p = ("product",)
    _section("01", "Product / material identity", "제품 / 원료 정보", lang,
             "Define the material, label basis and intended use before selecting tests.", "시험 선택 전에 물질 구분, 표시량 기준과 사용 목적을 기록하세요.")
    with st.container(border=True):
        _input(p, "material_type", lang, ["api", "excipient", "starting_material", "finished_product"])
        left, right = st.columns(2)
        with left:
            _input(p, "name", lang)
            _input(p, "api_name", lang)
            _input(p, "dosage_form", lang)
        with right:
            _input(p, "market", lang)
            _input(p, "claim_basis", lang, area=True)
        _input(p, "stage", lang)
        with st.expander("식별 정보 · 제조원 · 배치" if lang == "ko" else "Identifiers · manufacturer · batch"):
            for col, fields in zip(st.columns(2), (("identifier", "form", "route"), ("manufacturer", "batch"))):
                with col:
                    for field in fields:
                        _input(p, field, lang)
    _section("02", "Dose and whole-product basis", "투여량과 전체 제품 기준", lang,
             "API dose, unit strength, whole-product amount and analytical sample amount are distinct.", "API 투여량, 단위 표시량, 전체 제품량과 분석 시료량은 각각 다른 입력입니다.")
    dose, product = st.columns(2)
    with dose, st.container(border=True):
        st.markdown("**API 일일 투여량**" if lang == "ko" else "**API daily dose**")
        _input(p, "max_daily_api", lang, number=True)
        _input(p, "api_dose_unit", lang, list(MASS_MG))
        if s["product"]["material_type"] == "finished_product":
            _input(p, "strength", lang, number=True)
            _input(p, "strength_unit", lang, list(MASS_MG))
    with product, st.container(border=True):
        st.markdown("**전체 제품 / 원료 기여량**" if lang == "ko" else "**Whole product / material contribution**")
        if s["product"]["material_type"] == "finished_product":
            _input(p, "whole_unit", lang, number=True)
            _input(p, "whole_unit_unit", lang, [*MASS_MG, *VOLUME_ML])
            _input(p, "units_day", lang, number=True)
            if s["product"]["whole_unit_unit"] in VOLUME_ML:
                _input(p, "density", lang, number=True)
        else:
            _input(p, "max_daily_material", lang, number=True)
            _input(p, "material_dose_unit", lang, list(MASS_MG))
            st.caption("첨가제·출발물질 기여량은 임상 API 용량을 뜻하지 않습니다." if lang == "ko" else "Excipient / starting-material contribution does not establish a clinical API dose.")
    daily = daily_amounts(s["product"])
    a, b, c = st.columns(3)
    fmt = lambda v, u: ("미확인" if lang == "ko" else "Unknown") if v is None else f"{v:.12g} {u}"
    a.metric("입력 API 일일량" if lang == "ko" else "Entered API daily dose", fmt(daily["api_mg_day"], "mg/day"))
    b.metric("표시량 × 일일 단위수" if lang == "ko" else "Strength × units/day", fmt(daily["implied_api_mg_day"], "mg/day"))
    c.metric("완제 일일 질량 · 계산" if lang == "ko" else "Whole product daily mass · calculated", fmt(daily["whole_g_day"], "g/day"))
    for issue in daily["issues"]:
        st.warning(label(issue, lang))
    _provenance(s, list(s["product"]), "am_product_provenance", lang, "product_sources")

    _section("03", "Select test families", "시험항목 선택", lang,
             "Selection is a planning step. Applicability needs its own evidence review.", "선택은 계획 단계입니다. 적용성은 별도의 근거 검토가 필요합니다.")
    for offset in range(0, len(FAMILIES), 2):
        for col, (family, en, ko, keys) in zip(st.columns(2), FAMILIES[offset:offset+2]):
            if family == "other":
                keys = keys + [key for key in s["tests"] if key not in CATALOG]
            with col, st.container(border=True):
                widget_key = "am_family_" + family
                st.session_state[widget_key] = [key for key in keys if key in s["selected"]]
                st.pills(ko if lang == "ko" else en, keys, selection_mode="multi", key=widget_key,
                         format_func=lambda key: test_label(key, s, lang), width="stretch",
                         on_change=_select_family, args=(keys, widget_key))
    with st.expander("선택 목록 / 사용자 시험 추가" if lang == "ko" else "Selection list / add a custom test"):
        st.session_state.am_selected = list(s["selected"])
        st.multiselect("복수 시험항목" if lang == "ko" else "Multiple analytical tests", [*CATALOG, *[k for k in s["tests"] if k not in CATALOG]], key="am_selected", format_func=lambda k: test_label(k, s, lang), on_change=_select)
        st.text_input("사용자 시험항목명" if lang == "ko" else "Custom test name", key="am_custom_name")
        st.button("시험항목 추가" if lang == "ko" else "Add custom test", key="am_add_custom", on_click=_add_test)
        if st.session_state.get("am_custom_error"):
            st.warning(label(st.session_state.am_custom_error, lang))

def _test_record(key: str, lang: str) -> None:
    s = state()
    record = s["tests"][key]
    path = ("tests", key)
    _section("01", test_label(key, s, lang), test_label(key, s, lang), lang,
             CATALOG[key][2] if key in CATALOG else "", CATALOG[key][3] if key in CATALOG else "")
    fields = ("purpose", "rationale", "specification", "procedure", "preparation", "sst", "verification_plan", "validation_plan")
    missing = [label(f, lang) for f in fields if not record[f].strip()]
    complete = "입력 미완료" if lang == "ko" else "Inputs incomplete"
    if not missing:
        complete = "입력 기록됨" if lang == "ko" else "Inputs recorded"
    st.markdown(status_html([
        ("입력 항목" if lang == "ko" else "Input fields", complete, "근거·실험 확인은 별도" if lang == "ko" else "Evidence and experiments are separate"),
        ("근거 확인" if lang == "ko" else "Source verification", label("reviewed" if record.get("evidence_review") else "pending", lang), label(record["applicability"], lang)),
        ("실험적 뒷받침" if lang == "ko" else "Experimental support", label("reviewed" if record.get("experiment_review") else "pending", lang), "QC 사용 승인 아님" if lang == "ko" else "Not QC use approval"),
    ]), unsafe_allow_html=True)
    if missing:
        _gap(("필요한 입력: " if lang == "ko" else "Missing inputs: ") + ", ".join(missing))
    with st.container(border=True):
        _input(path, "purpose", lang)
        left, right = st.columns(2)
        with left:
            _input(path, "applicability", lang, ["pending", "applicable", "not_applicable"])
        with right:
            _input(path, "source_type", lang, ["compendial", "manufacturer_source", "approved", "proposal", "experimental"])
        _input(path, "rationale", lang, area=True)
    _section("02", "Source and method record", "출처와 시험법 기록", lang,
             "Record the current source and scope; the selected catalog does not supply a method.", "현행 원문과 적용 범위를 기록합니다. 선택한 시험 목록이 시험법을 제공하지 않습니다.")
    with st.expander("원문 · 버전 · 적용 범위" if lang == "ko" else "Source · version · application scope", expanded=True):
        for col, fields in zip(st.columns(2), (("source", "version", "location"), ("scope", "excerpt"))):
            with col:
                for field in fields:
                    _input(path, field, lang, area=field in {"source", "scope", "excerpt"})
        _input(path, "value_kind", lang, ["entered", "source_derived", "proposal", "example"])
    for en, ko, fields in [
        ("Specification and system suitability", "규격과 시스템적합성", ("specification", "sst")),
        ("Procedure and preparation", "분석절차와 조제법", ("procedure", "preparation")),
        ("Verification, validation and experimental support", "검증·밸리데이션과 실험 근거", ("verification_plan", "validation_plan", "experimental_data")),
    ]:
        count = sum(not record[f].strip() for f in fields)
        suffix = (f" · {count}개 미기록" if lang == "ko" else f" · {count} unrecorded") if count else ""
        with st.expander((ko if lang == "ko" else en) + suffix):
            for field in fields:
                _input(path, field, lang, area=True)
    _provenance(record, ["purpose", "specification", "procedure", "preparation", "sst", "verification_plan", "validation_plan"], "am_method_origins_" + key, lang, "input_sources")
    with st.expander("Q14 접근법과 독립 검토 기록" if lang == "ko" else "Q14 approach and independent review records"):
        _input(path, "approach", lang, ["minimal", "enhanced"])
        st.caption("Q14 최소 접근법도 가능합니다. 정식 ATP 문서·DoE·MODR은 보편적 필수사항이 아닙니다. Q2(R2)는 성능 검증, Q6는 규격, Q3/M7은 불순물 노출·관리 근거입니다." if lang == "ko" else "Q14 permits a minimal approach. A formal ATP document, DoE and MODR are not universal requirements. Q2(R2) addresses validation, Q6 specifications, and Q3/M7 impurity exposure and controls.")
        source, experimental = st.columns(2)
        with source:
            st.markdown("**근거 확인**" if lang == "ko" else "**Source verification**")
            _review(key, "evidence", lang)
        with experimental:
            st.markdown("**실험적 뒷받침**" if lang == "ko" else "**Experimental support**")
            _review(key, "experiment", lang)
    with st.expander("DMF / 제조원 자료 대조 · 미검토" if lang == "ko" else "DMF / supplier comparison · unreviewed"):
        st.info(label("dmf_pending", lang))
        for field in ("source", "version", "location", "scope"):
            _input(("dmf",), field, lang)
        for field in ("supplier_specification", "supplier_procedure", "supplier_preparation", "supplier_impurities", "comparison_action"):
            _input(path, field, lang, area=True)
        st.dataframe(pd.DataFrame(comparison_rows(record, lang), columns=["항목", "기초안", "제조원", "차이 상태"] if lang == "ko" else ["Field", "Baseline", "Supplier", "Comparison state"]), hide_index=True, width="stretch")

def _preparation(key: str, kind: str, lang: str) -> None:
    s = state()
    prep = s["tests"][key][kind]
    path = ("tests", key, kind)
    with st.container(border=True):
        _section("S" if kind == "sample" else "R", label(kind, lang), label(kind, lang), lang)
        st.caption(label("reviewed" if prep.get("review") else "pending", lang) + " · " + label(prep["value_kind"], lang))
        fmt = lambda v: ("미확인" if lang == "ko" else "Unknown") if v is None else f"{v:.12g}"
        assumptions = [label(prep["correction_mode"], lang), label("basis_factor", lang) + ": " + fmt(prep.get("basis_factor"))]
        if prep["correction_mode"] != "none":
            assumptions.append(label("potency", lang) + ": " + fmt(prep.get("potency")))
        if prep["correction_mode"] == "dry":
            assumptions.append(label("water", lang) + ": " + fmt(prep.get("water")))
        if kind == "sample":
            assumptions.append(label("extraction", lang) + ": " + fmt(prep.get("extraction")))
        st.caption(" · ".join(assumptions))
        flow = st.empty()
        missing_slot = st.empty()
        basis_options = ["direct_analyte"] if kind == "reference" else ["direct_analyte", "product_mass", "product_volume", "whole_matrix"]
        _input(path, "basis", lang, basis_options)
        amount, unit = st.columns([1.3, 1])
        with amount:
            _input(path, "amount", lang, number=True)
        with unit:
            _input(path, "amount_unit", lang, [*MASS_MG, *VOLUME_ML] if kind == "sample" else list(MASS_MG))
        _input(path, "stock_ml", lang, number=True)
        with st.expander("역가 · 추출 · 염 환산 기준" if lang == "ko" else "Potency · extraction · analyte conversion"):
            _input(path, "correction_mode", lang, ["none", "as_is", "dry"])
            if prep["correction_mode"] != "none":
                _input(path, "potency", lang, number=True)
            if prep["correction_mode"] == "dry":
                _input(path, "water", lang, number=True)
            _input(path, "basis_factor", lang, number=True)
            _input(path, "basis_note", lang, area=True)
            if kind == "sample":
                _input(path, "extraction", lang, number=True)
                st.caption("추출 분율은 명시적 계산 가정입니다. 회수율 측정값을 자동 보정에 사용하지 않습니다." if lang == "ko" else "Extraction fraction is an explicit calculation assumption. Measured recovery is not automatically used as a correction.")
        st.markdown("**연속 희석 · 각 행은 한 단계**" if lang == "ko" else "**Serial dilution · one step per row**")
        st.caption("분취량 → 희석 후 최종부피 (mL). 희석이 없으면 표를 비워두세요." if lang == "ko" else "Aliquot → diluted final volume (mL). Leave the table empty when there is no dilution.")
        step_key = _step_widget_key(key, kind, lang)
        columns = {k: label(k, lang) for k in ("aliquot_ml", "final_ml")}
        frame = pd.DataFrame(prep["steps"], columns=list(columns)).rename(columns=columns)
        edited = st.data_editor(frame, num_rows="dynamic", hide_index=True, key=step_key, width="stretch",
            on_change=_step_change, args=(key, kind, step_key, deepcopy(prep["steps"]), lang),
            column_config={v: st.column_config.NumberColumn(v, min_value=0.0, required=True) for v in columns.values()})
        next_steps = edited.astype(object).where(pd.notnull(edited), None).rename(columns={v: k for k, v in columns.items()}).to_dict("records")
        if next_steps != prep["steps"]:
            # Also handles programmatically supplied/testing editor state. New revision
            # consumes each delta once, including additions/deletions and blank cells.
            _replace_steps(key, kind, next_steps)
            st.rerun()
        with st.expander("조제 근거와 값별 출처" if lang == "ko" else "Preparation basis and per-value sources"):
            _input(path, "value_kind", lang, ["entered", "source_derived", "proposal", "example"])
            for field in ("source", "version", "location"):
                _input(path, field, lang)
            _provenance(prep, ["amount", "amount_unit", "basis", "correction_mode", "potency", "water", "basis_factor", "extraction", "stock_ml"], "am_prep_origins_" + key + "_" + kind, lang, "input_sources")
        refresh_reviews(s)
        missing = missing_preparation(prep, s["product"], kind == "reference")
        if missing:
            text = ("계산에 필요한 입력: " if lang == "ko" else "Calculation needs: ") + ", ".join(label(f, lang) for f in missing)
            missing_slot.markdown('<div class="am-missing">' + escape(text) + '</div>', unsafe_allow_html=True)
        calc = None
        try:
            calc = calculate_preparation(prep, s["product"], kind == "reference")
            if calc["matrix_g_ml"] is not None:
                st.metric("전체 매트릭스 농도 (계산)" if lang == "ko" else "Whole-matrix concentration (calculated)", f"{calc['matrix_g_ml']:.12g} g/mL")
                st.caption("분석대상 농도와 별도 · 계산 검토 상태 별도" if lang == "ko" else "Separate from analyte concentration · calculation review separate")
            else:
                st.metric("최종 농도 (계산)" if lang == "ko" else "Final concentration (calculated)", f"{calc['final_ug_ml']:.12g} ug/mL")
            with st.expander("전체 수식 · 대입값 · 단위 확인" if lang == "ko" else "Complete equation · substitutions · units", expanded=True):
                st.code(calc["formula"] + "\n" + "\n".join(calc["trace"]), language=None, wrap_lines=True)
        except (ValueError, TypeError, OverflowError) as exc:
            st.info(label("incomplete", lang) + ": " + label(str(exc), lang))
        flow.markdown(flow_html(prep, calc, lang), unsafe_allow_html=True)
        with st.expander("독립 계산 검토 기록" if lang == "ko" else "Independent calculation review record"):
            _review(key, kind, lang)

def _limit(lang: str) -> None:
    st.subheader("불순물 허용 노출량 환산" if lang == "ko" else "Impurity exposure allowance conversion")
    st.caption("확인한 물질별 AI / 경로별 PDE 등과 출처를 직접 입력하세요. 니트로사민에 일반 TTC를 자동 적용하지 않습니다. API와 완제 일일 질량 분모를 바꾸어 쓰지 않습니다." if lang == "ko" else "Enter the verified compound-specific AI / route-specific PDE and source. No general TTC is applied to nitrosamines. API and whole-product daily-mass denominators are distinct.")
    for field in ("limit_kind", "source", "version", "location", "scope"):
        _input(("limit",), field, lang)
    _input(("limit",), "allowance", lang, number=True)
    _input(("limit",), "denominator", lang, ["whole_product", "api_daily", "material_daily"])
    try:
        result = impurity_limit(state())
        st.metric("계산 농도 한도; 적용성 미확인" if lang == "ko" else "Calculated concentration limit; applicability unverified", f"{result['ug_g']:.12g} ug/g")
        st.code(result["equation"], language=None)
    except ValueError as exc:
        st.info(label("pending", lang) + ": " + label(str(exc), lang))
    matrix_keys = [key for key in state()["selected"] if state()["tests"][key]["sample"]["basis"] == "whole_matrix"]
    if matrix_keys:
        chosen = st.selectbox("J 환산용 매트릭스 조제" if lang == "ko" else "Matrix preparation for J conversion", matrix_keys, key="am_j_test", format_func=lambda k: test_label(k, state(), lang))
        try:
            st.code(impurity_limit(state(), state()["tests"][chosen]["sample"])["equation"], language=None)
        except (ValueError, TypeError, OverflowError) as exc:
            st.info(label(str(exc), lang))

def render(lang: str) -> None:
    s = state()
    st.markdown(STYLE, unsafe_allow_html=True)
    title = "분석법 작업공간" if lang == "ko" else "Analytical method workspace"
    description = "원료와 완제의 기준을 구분하고, 시험법 근거와 조제 계산을 독립적으로 검토하세요." if lang == "ko" else "Separate material and product bases, then review method evidence and preparation calculations independently."
    st.markdown(f'<section class="am-heading"><div class="am-kicker">METHOD DEVELOPMENT / REVIEW</div><h2>{title}</h2><p>{description}</p><div class="am-legend"><span class="am-tag">{label("entered", lang)}</span><span class="am-tag source">{label("source_derived", lang)}</span><span class="am-tag calc">{label("calculated", lang)}</span></div></section>', unsafe_allow_html=True)
    if s["example"]:
        st.warning(label("example", lang))
    else:
        st.caption("원문 확인 · 실험 근거 · 계산 검토는 각각 기록합니다. 미확인 값은 비워두세요." if lang == "ko" else "Source verification, experiments and calculation review are separate. Leave unknown values blank.")
    tabs = st.tabs(["01 제품·시험", "02 시험법·근거", "03 검액·표준액", "04 한도·보고서"] if lang == "ko" else ["01 Product & tests", "02 Methods & evidence", "03 Concentrations", "04 Limits & reports"])
    with tabs[0]:
        _product(lang)
    if s["selected"]:
        with tabs[1]:
            selected = _input((), "active_method_test", lang, s["selected"])
            _test_record(selected, lang)
        with tabs[2]:
            selected = _input((), "active_calculation_test", lang, s["selected"])
            st.caption("각 흐름의 계산값은 전체 입력이 유효할 때만 표시됩니다. 최종 농도가 계산되어도 독립 검토는 별도입니다." if lang == "ko" else "Flow values appear only when the complete preparation is valid. A calculated concentration still needs its own independent review.")
            sample, reference = st.columns(2)
            with sample:
                _preparation(selected, "sample", lang)
            with reference:
                _preparation(selected, "reference", lang)
    else:
        with tabs[1]:
            st.info("먼저 시험항목을 선택하세요." if lang == "ko" else "Select a test first.")
        with tabs[2]:
            st.info("먼저 시험항목을 선택하세요." if lang == "ko" else "Select a test first.")
    with tabs[3]:
        _limit(lang)
        _section("02", "Export the review record", "검토 기록 내보내기", lang,
                 "Exports retain inputs, equations, source gaps and review states.", "입력값, 수식, 근거 누락과 검토 상태를 함께 내보냅니다.")
        report = report_markdown(s, lang)
        with st.container(horizontal=True):
            st.download_button("보고서 · Markdown" if lang == "ko" else "Report · Markdown", report.encode("utf-8"), file_name=f"VCC_Analytical_Method_{lang}.md", mime="text/markdown", key="am_report_download")
            st.download_button("수식 포함 Excel" if lang == "ko" else "Excel with formulas", export_workbook(s, lang), file_name=f"VCC_Analytical_Method_{lang}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="am_excel_download")
            st.download_button("입력·검토 JSON" if lang == "ko" else "Inputs / reviews · JSON", json.dumps(s, ensure_ascii=False, indent=2, allow_nan=False).encode(), file_name=f"VCC_Analytical_Method_{lang}.json", mime="application/json", key="am_json_download")
        with st.expander("보고서 미리보기" if lang == "ko" else "Report preview"):
            st.markdown(report)
    with st.expander("예시와 작업공간 정보" if lang == "ko" else "Demo and workspace details"):
        st.caption(UI_BUILD + " · " + BUILD)
        st.button("가상 정제 예시 불러오기 (이 작업공간 대체)" if lang == "ko" else "Load fictional tablet demo (replace this workspace)", key="am_demo", on_click=_demo)
        st.caption("이 버튼은 현재 작업공간을 대체합니다. 예시에는 검증되지 않은 가상 수치만 있습니다." if lang == "ko" else "This button replaces the current workspace. The demo contains fictional, unvalidated values.")

def apply_analytical_workspace(app: Any) -> None:
    if getattr(app, "_analytical_workspace_applied", False):
        return
    app.TEXT["ko"]["analytical_method"] = "분석법 작업공간"
    app.TEXT["en"]["analytical_method"] = "Analytical method workspace"
    app.NAV_ITEMS.insert(0, {"key": "method", "label_key": "analytical_method", "description": "Material / product, methods and independent calculations", "description_ko": "원료 / 완제, 시험법 및 독립 계산", "icon": "vial", "tone": "teal"})
    original_page = app.render_selected_page
    original_packet = app.build_decision_packet
    def page(page_key: str, lang: str, profile: dict[str, Any]) -> None:
        if page_key == "method":
            render(lang)
        else:
            original_page(page_key, lang, profile)
    def packet(profile: dict[str, Any]) -> str:
        text = original_packet(profile)
        if STATE_KEY in st.session_state:
            text += "\n\n" + report_markdown(state(), st.session_state.get("lang", "en"))
        return text
    app.render_selected_page = page
    app.build_decision_packet = packet
    app.APP_BUILD = UI_BUILD
    app._analytical_workspace_applied = True

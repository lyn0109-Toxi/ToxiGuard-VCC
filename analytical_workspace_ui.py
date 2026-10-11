"""Korean / English analytical-method workspace for the existing Streamlit app."""
from __future__ import annotations

from copy import deepcopy
import json
from typing import Any

import pandas as pd
import streamlit as st

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
        saved = {row["field"]: row for row in record.get(stored_field, [])}
        rows = [{"field": field, "value_kind": saved.get(field, {}).get("value_kind", "entered"), **{k: saved.get(field, {}).get(k, "") for k in ("source", "version", "location", "basis_note")}} for field in fields]
        columns = ["field", "value_kind", "source", "version", "location", "basis_note"]
        names = {"field": "입력 항목" if lang == "ko" else "Input field", **{k: label(k, lang) for k in columns[1:]}}
        df = pd.DataFrame(rows, columns=columns)
        kinds = ["entered", "source_derived", "proposal", "example"]
        localized = df.copy()
        localized["field"] = localized["field"].map(lambda v: label(v, lang))
        localized["value_kind"] = localized["value_kind"].map(lambda v: label(v, lang))
        edited = st.data_editor(localized.rename(columns=names), hide_index=True, width="stretch", disabled=[names["field"]], key=key + "_" + lang,
            column_config={names["value_kind"]: st.column_config.SelectboxColumn(options=[label(v, lang) for v in kinds], required=True)})
        edited = edited.rename(columns={v: k for k, v in names.items()})
        edited["field"] = fields
        reverse = {label(v, lang): v for v in kinds}
        edited["value_kind"] = edited["value_kind"].map(reverse)
        record[stored_field] = edited.fillna("").to_dict("records")
        refresh_reviews(state())

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
    st.subheader("01 · 제품 / 원료 정보" if lang == "ko" else "01 · Product / material inputs")
    _input(p, "material_type", lang, ["api", "excipient", "starting_material", "finished_product"])
    for col, fields in zip(st.columns(3), (("name", "api_name", "identifier", "form"), ("claim_basis", "dosage_form", "route", "market"), ("manufacturer", "batch", "stage"))):
        with col:
            for field in fields:
                _input(p, field, lang)
    st.caption("API 투여량, 투여단위 표시량, 전체 제품량, 분석 시료량을 각각 입력합니다." if lang == "ko" else "API daily dose, dosage-unit strength, whole product amount and analytical sample amount are separate inputs.")
    with st.container(border=True):
        dose, product = st.columns(2)
        with dose:
            _input(p, "max_daily_api", lang, number=True)
            _input(p, "api_dose_unit", lang, list(MASS_MG))
        with product:
            if s["product"]["material_type"] == "finished_product":
                _input(p, "strength", lang, number=True)
                _input(p, "strength_unit", lang, list(MASS_MG))
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
        fmt = lambda v, u: "—" if v is None else f"{v:.12g} {u}"
        a.metric("입력 API 일일량" if lang == "ko" else "Entered API daily dose", fmt(daily["api_mg_day"], "mg/day"))
        b.metric("표시량 × 투여단위수 (계산)" if lang == "ko" else "Strength × units/day (calculated)", fmt(daily["implied_api_mg_day"], "mg/day"))
        c.metric("완제 일일 질량 (계산)" if lang == "ko" else "Whole product daily mass (calculated)", fmt(daily["whole_g_day"], "g/day"))
        for issue in daily["issues"]:
            st.warning(label(issue, lang))
    _provenance(s, list(s["product"]), "am_product_provenance", lang, "product_sources")

    st.subheader("02 · 시험항목 선택" if lang == "ko" else "02 · Select analytical tests")
    st.info("선택은 적용성 확인을 뜻하지 않습니다. 실제 각조·제형·시장·공정과 실험실 조건에 따라 근거를 기록하세요." if lang == "ko" else "Selection does not establish applicability. Record the actual monograph, dosage form, market, process and laboratory basis.")
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
    st.subheader(test_label(key, s, lang))
    if key in CATALOG:
        st.caption(CATALOG[key][3 if lang == "ko" else 2])
    _input(path, "purpose", lang)
    _input(path, "applicability", lang, ["pending", "applicable", "not_applicable"])
    _input(path, "rationale", lang)
    _input(path, "source_type", lang, ["compendial", "manufacturer_source", "approved", "proposal", "experimental"])
    _input(path, "value_kind", lang, ["entered", "source_derived", "proposal", "example"])
    for col, fields in zip(st.columns(2), (("source", "version", "location"), ("scope", "excerpt"))):
        with col:
            for field in fields:
                _input(path, field, lang, area=field == "excerpt")
    for field in ("specification", "procedure", "preparation", "sst", "verification_plan", "validation_plan", "experimental_data"):
        _input(path, field, lang, area=True)
    _provenance(record, ["purpose", "specification", "procedure", "preparation", "sst", "verification_plan", "validation_plan"], "am_method_origins_" + key, lang, "input_sources")
    _input(path, "approach", lang, ["minimal", "enhanced"])
    st.caption("Q14 최소 접근법도 가능합니다. 정식 ATP 문서·DoE·MODR은 보편적 필수사항이 아닙니다. Q2(R2)는 성능 검증, Q6는 규격, Q3/M7은 불순물 노출·관리 근거입니다." if lang == "ko" else "Q14 permits a minimal approach. A formal ATP document, DoE and MODR are not universal requirements. Q2(R2) addresses validation, Q6 specifications, and Q3/M7 impurity exposure and controls.")
    fields = ("purpose", "rationale", "specification", "procedure", "preparation", "sst", "verification_plan", "validation_plan")
    missing = [label(f, lang) for f in fields if not record[f].strip()]
    st.caption(("입력 미완료: " if lang == "ko" else "Inputs incomplete: ") + ", ".join(missing) if missing else ("입력 항목 기록됨; 근거·실험 확인은 별도" if lang == "ko" else "Input fields recorded; evidence and experimental support remain separate"))
    source, experimental = st.columns(2)
    with source:
        st.markdown("**근거 확인**" if lang == "ko" else "**Source verification**")
        _review(key, "evidence", lang)
    with experimental:
        st.markdown("**실험적 뒷받침**" if lang == "ko" else "**Experimental support**")
        _review(key, "experiment", lang)
    with st.expander("DMF / 제조원 자료 대조" if lang == "ko" else "DMF / supplier source comparison"):
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
    st.subheader(label(kind, lang))
    basis_options = ["direct_analyte"] if kind == "reference" else ["direct_analyte", "product_mass", "product_volume", "whole_matrix"]
    _input(path, "basis", lang, basis_options)
    _input(path, "amount", lang, number=True)
    _input(path, "amount_unit", lang, [*MASS_MG, *VOLUME_ML] if kind == "sample" else list(MASS_MG))
    _input(path, "correction_mode", lang, ["none", "as_is", "dry"])
    if prep["correction_mode"] != "none":
        _input(path, "potency", lang, number=True)
    if prep["correction_mode"] == "dry":
        _input(path, "water", lang, number=True)
    _input(path, "basis_factor", lang, number=True)
    _input(path, "basis_note", lang)
    if kind == "sample":
        _input(path, "extraction", lang, number=True)
        st.caption("추출 분율은 명시적 계산 가정입니다. 회수율 측정값을 자동 보정에 사용하지 않습니다." if lang == "ko" else "Extraction fraction is an explicit calculation assumption. Measured recovery is not automatically used as a correction.")
    _input(path, "stock_ml", lang, number=True)
    step_key = "am_steps_" + key + "_" + kind + "_" + lang
    columns = {k: label(k, lang) for k in ("aliquot_ml", "final_ml")}
    frame = pd.DataFrame(prep["steps"], columns=list(columns)).rename(columns=columns)
    edited = st.data_editor(frame, num_rows="dynamic", hide_index=True, key=step_key, width="stretch",
        column_config={v: st.column_config.NumberColumn(v, min_value=0.0, required=True) for v in columns.values()})
    prep["steps"] = edited.astype(object).where(pd.notnull(edited), None).rename(columns={v: k for k, v in columns.items()}).to_dict("records")
    _input(path, "value_kind", lang, ["entered", "source_derived", "proposal", "example"])
    for field in ("source", "version", "location"):
        _input(path, field, lang)
    _provenance(prep, ["amount", "amount_unit", "basis", "correction_mode", "potency", "water", "basis_factor", "extraction", "stock_ml"], "am_prep_origins_" + key + "_" + kind, lang, "input_sources")
    refresh_reviews(s)
    try:
        calc = calculate_preparation(prep, s["product"], kind == "reference")
        st.metric("최종 농도 (계산)" if lang == "ko" else "Final concentration (calculated)", f"{calc['final_ug_ml']:.12g} ug/mL")
        if calc["matrix_g_ml"] is not None:
            st.caption(f"{calc['matrix_g_ml']:.12g} g/mL " + ("전체 매트릭스" if lang == "ko" else "whole matrix"))
        st.code(calc["formula"] + "\n" + "\n".join(calc["trace"]), language=None, wrap_lines=True)
    except (ValueError, TypeError, OverflowError) as exc:
        st.info(label("incomplete", lang) + ": " + label(str(exc), lang))
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
    st.header("분석법 작업공간" if lang == "ko" else "Analytical method workspace")
    st.caption(BUILD)
    st.button("가상 정제 예시 불러오기 (이 작업공간 대체)" if lang == "ko" else "Load fictional tablet demo (replace this workspace)", key="am_demo", on_click=_demo)
    if s["example"]:
        st.warning(label("example", lang))
    else:
        st.info("빈 작업공간입니다. 원문 확인과 실험 근거는 각각 기록합니다." if lang == "ko" else "This workspace starts blank. Source verification and experimental support are recorded separately.")
    tabs = st.tabs(["제품·시험항목", "시험법·근거", "검액·표준액 독립 계산", "노출 한도·보고서"] if lang == "ko" else ["Product & tests", "Method & evidence", "Independent sample & reference", "Exposure & reports"])
    with tabs[0]:
        _product(lang)
    if s["selected"]:
        with tabs[1]:
            selected = _input((), "active_method_test", lang, s["selected"])
            _test_record(selected, lang)
        with tabs[2]:
            selected = _input((), "active_calculation_test", lang, s["selected"])
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
        report = report_markdown(s, lang)
        st.download_button("분석법 보고서 다운로드" if lang == "ko" else "Download analytical method report", report.encode("utf-8"), file_name=f"VCC_Analytical_Method_{lang}.md", mime="text/markdown", key="am_report_download")
        st.download_button("수식 포함 Excel 다운로드" if lang == "ko" else "Download Excel with formulas", export_workbook(s, lang), file_name=f"VCC_Analytical_Method_{lang}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="am_excel_download")
        st.download_button("입력·검토 JSON 다운로드" if lang == "ko" else "Download input / review JSON", json.dumps(s, ensure_ascii=False, indent=2, allow_nan=False).encode(), file_name=f"VCC_Analytical_Method_{lang}.json", mime="application/json", key="am_json_download")
        with st.expander("보고서 미리보기" if lang == "ko" else "Report preview"):
            st.markdown(report)

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
    app.APP_BUILD = BUILD
    app._analytical_workspace_applied = True

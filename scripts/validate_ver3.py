from __future__ import annotations

from pathlib import Path
import re
import sys

import pandas as pd
from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "streamlit_app.py"


def collect_visible_text(page: AppTest) -> str:
    blocks: list[str] = []
    for collection_name in [
        "title",
        "header",
        "subheader",
        "markdown",
        "info",
        "warning",
        "success",
        "error",
        "caption",
        "button",
        "selectbox",
        "number_input",
        "text_input",
        "text_area",
        "dataframe",
        "data_editor",
    ]:
        collection = getattr(page, collection_name, [])
        blocks += [getattr(item, "value", "") for item in collection]
        blocks += [getattr(item, "label", "") for item in collection]
    return "\n".join(str(block) for block in blocks if block is not None and str(block))


def assert_no_exception(page: AppTest) -> None:
    if page.exception:
        raise AssertionError(page.exception)


def query_param(page: AppTest, key: str) -> str:
    value = page.query_params.get(key, "")
    return str(value[0] if isinstance(value, list) and value else value)


def assert_current_page(page: AppTest, expected: str) -> None:
    assert_no_exception(page)
    if page.session_state["active_page"] != expected:
        raise AssertionError(f"Expected active page {expected}, got {page.session_state['active_page']}")
    if query_param(page, "page") != expected:
        raise AssertionError(f"Navigation did not synchronize the URL to {expected}")
    if page.selectbox(key="detail_page_widget").value != expected:
        raise AssertionError(f"Detailed page selector did not synchronize to {expected}")


def assert_landing_and_entry() -> AppTest:
    default = AppTest.from_file(str(APP)).run(timeout=30)
    assert_no_exception(default)
    if default.radio(key="language_choice").value != "en":
        raise AssertionError("A fresh landing must default to English")
    if default.button(key="landing_enter_button").label != "Start document review":
        raise AssertionError("Default landing must expose an English start action")
    default.button(key="landing_enter_button").click().run(timeout=30)
    assert_current_page(default, "intake")
    if default.session_state["lang"] != "en":
        raise AssertionError("Default English must persist into the workbench")

    landing = AppTest.from_file(str(APP))
    landing.query_params["lang"] = "ko"
    landing.run(timeout=30)
    assert_no_exception(landing)
    text = collect_visible_text(landing)
    # Test that purpose and results are readable text, without tying the test to
    # one exact headline or a decorative image/CSS implementation.
    if not all(fragment in text for fragment in ("CMC", "CTD", "검토")):
        raise AssertionError("Landing must explain its CMC/CTD review purpose in Korean")
    for key in ("landing_enter_button", "landing_validation_button", "landing_preview_button"):
        button = landing.button(key=key)
        if button.disabled or not re.search(r"[가-힣]", button.label):
            raise AssertionError(f"Landing action {key} must be enabled with a Korean accessible label")
    landing.button(key="landing_enter_button").click().run(timeout=30)
    assert_current_page(landing, "intake")
    if landing.session_state["lang"] != "ko":
        raise AssertionError("Entry must retain explicitly selected Korean")
    if "intake_editor" not in {getattr(item, "key", None) for item in landing.get("dataframe")}:
        # AppTest versions can expose data_editor as an unknown element. Its
        # registered state proves the intake editor has actually been rendered.
        if "intake_editor" not in landing.session_state:
            raise AssertionError("The primary start action did not open intake editing")

    preview = AppTest.from_file(str(APP))
    preview.query_params["lang"] = "ko"
    preview.run(timeout=30)
    preview.button(key="landing_preview_button").click().run(timeout=30)
    assert_current_page(preview, "response")
    if "검토 메모 미리보기" not in collect_visible_text(preview):
        raise AssertionError("The preview action did not open the reusable result")

    validation = AppTest.from_file(str(APP)).run(timeout=30)
    validation.button(key="landing_validation_button").click().run(timeout=30)
    assert_current_page(validation, "validation")
    if validation.number_input(key="ext_prep_assay_weighed").value != 25.0:
        raise AssertionError("Direct validation entry did not expose the existing calculation controls")

    english = AppTest.from_file(str(APP))
    english.query_params["lang"] = "en"
    english.run(timeout=30)
    assert_no_exception(english)
    if re.search(r"[가-힣]", english.button(key="landing_enter_button").label):
        raise AssertionError("An explicit English URL must render English entry actions")
    english.button(key="landing_enter_button").click().run(timeout=30)
    assert_current_page(english, "intake")
    if english.session_state["lang"] != "en":
        raise AssertionError("Entry must retain an explicitly chosen language")
    return landing


def assert_navigation_and_session_persistence(page: AppTest) -> None:
    import app as app_module

    expected_pages = {str(item["key"]) for item in app_module.NAV_ITEMS}
    detail = page.selectbox(key="detail_page_widget")
    if len(detail.options) != len(expected_pages):
        raise AssertionError("All existing review pages must remain reachable from the detail selector")
    product = "VCC persistence fixture — 제품 A"
    intake_question = "Fixture: confirm the current source version"
    source_excerpt = "Fixture source: DMF version 7, confirmed 2026-09-28"
    page.text_input(key="profile_product").set_value(product).run(timeout=30)
    assert_no_exception(page)
    if page.session_state["profile_values"]["product"] != product:
        raise AssertionError("Product changes were not saved outside widget state")

    # AppTest does not yet provide data_editor.set_value. Supply the frontend
    # edit delta, then exercise the real editor/localization/state-save path.
    page.session_state["intake_editor"] = {
        "edited_rows": {0: {
            app_module.COLUMN_KO["Received"]: app_module.localize_value("Received", "ko"),
            app_module.COLUMN_KO["Client question"]: intake_question,
        }},
        "added_rows": [], "deleted_rows": [],
    }
    page.run(timeout=30)
    assert_no_exception(page)
    intake = page.session_state["intake_df"].copy(deep=True)
    if intake.iloc[0]["Received"] != "Received" or intake.iloc[0]["Client question"] != intake_question:
        raise AssertionError("An intake edit was not saved in canonical form")

    def assert_saved() -> None:
        assert_no_exception(page)
        if page.session_state["profile_values"]["product"] != product:
            raise AssertionError("Navigation or language change reset the product profile")
        if page.session_state["active_page"] != "case" and page.text_input(key="profile_product").value != product:
            raise AssertionError("Visible workbench profile diverged from saved project")
        pd.testing.assert_frame_equal(page.session_state["intake_df"], intake, obj="Saved intake table")

    for destination in ("dashboard", "validation", "response", "intake"):
        page.button(key=f"workflow_{destination}").click().run(timeout=30)
        assert_current_page(page, destination)
        assert_saved()

    page.button(key="open_document_sources").click().run(timeout=30)
    assert_current_page(page, "documents")
    assert_saved()
    page.session_state["dmf_source_editor"] = {
        "edited_rows": {0: {app_module.COLUMN_KO["Document text / excerpt"]: source_excerpt}},
        "added_rows": [], "deleted_rows": [],
    }
    page.run(timeout=30)
    assert_no_exception(page)
    source = page.session_state["dmf_source_df"].copy(deep=True)
    if source.iloc[0]["Document text / excerpt"] != source_excerpt:
        raise AssertionError("The entered source excerpt was not saved")
    ctd = page.session_state["ctd_document_df"].copy(deep=True)

    # Switch the actual language widget rather than setting lang in state;
    # widget identity changes previously reset edited product inputs.
    for lang in ("en", "ko"):
        language_control = page.radio(key="language_choice")
        if not {"한국어", "English"}.issubset(set(language_control.options)):
            raise AssertionError("Expected readable Korean/English language choices")
        language_control.set_value(lang).run(timeout=30)
        assert_current_page(page, "documents")
        if page.session_state["lang"] != lang or query_param(page, "lang") != lang:
            raise AssertionError(f"Language selection did not persist as {lang}")
        assert_saved()
        pd.testing.assert_frame_equal(page.session_state["dmf_source_df"], source, obj="Saved source table")
        pd.testing.assert_frame_equal(page.session_state["ctd_document_df"], ctd, obj="Saved CTD table")

    # Traverse every native detail option in a single session to catch resets
    # that fresh-page smoke tests cannot detect.
    for destination in [str(item["key"]) for item in app_module.NAV_ITEMS]:
        page.selectbox(key="detail_page_widget").set_value(destination).run(timeout=30)
        assert_current_page(page, destination)
        assert_saved()
        pd.testing.assert_frame_equal(page.session_state["dmf_source_df"], source, obj="Saved source table")
        pd.testing.assert_frame_equal(page.session_state["ctd_document_df"], ctd, obj="Saved CTD table")


def assert_calculation_inputs_survive_navigation() -> None:
    page = AppTest.from_file(str(APP))
    page.query_params.update({"enter": "1", "page": "validation", "lang": "ko"})
    page.run(timeout=30)
    assert_current_page(page, "validation")
    weighed_key = "ext_prep_assay_weighed"
    page.number_input(key=weighed_key).set_value(40.0).run(timeout=30)
    assert_no_exception(page)
    saved_calculation = dict(page.session_state["last_calc"])
    # 40 mg at 99.8%, 100 mL stock, 1 mL aliquot / 50 mL / 2 dilution.
    if abs(float(saved_calculation["final_conc"]) - 3.992) > 1e-9:
        raise AssertionError("The edited assay input did not reach the calculation")

    def assert_assay_restored() -> None:
        assert_current_page(page, "validation")
        if page.session_state["validation_test_item"] != "assay":
            raise AssertionError("Assay was not restored as the selected test")
        if page.number_input(key=weighed_key).value != 40.0:
            raise AssertionError("The assay weighing input reset after it was hidden")
        if page.session_state["last_calc"] != saved_calculation:
            raise AssertionError("Returning to assay changed the saved calculation")

    page.button(key="workflow_dashboard").click().run(timeout=30)
    assert_current_page(page, "dashboard")
    if page.session_state["last_calc"] != saved_calculation:
        raise AssertionError("Leaving validation discarded its calculation")
    page.selectbox(key="detail_page_widget").set_value("validation").run(timeout=30)
    assert_assay_restored()

    page.button(key="vcc_ext_related_substances").click().run(timeout=30)
    assert_no_exception(page)
    if page.session_state["validation_test_item"] != "related_substances":
        raise AssertionError("The test selector did not open related substances")
    page.number_input(key="related_mdd_mg_day").set_value(125.0).run(timeout=30)
    assert_no_exception(page)
    page.button(key="vcc_ext_assay").click().run(timeout=30)
    assert_assay_restored()
    page.button(key="vcc_ext_related_substances").click().run(timeout=30)
    assert_no_exception(page)
    if page.number_input(key="related_mdd_mg_day").value != 125.0:
        raise AssertionError("The related-substance daily dose reset after changing tests")
    page.button(key="vcc_ext_assay").click().run(timeout=30)
    assert_assay_restored()


def assert_edited_validation_criteria_and_q14_survive_navigation() -> None:
    import app as app_module
    from validation_extension import evaluate_q14_problem

    page = AppTest.from_file(str(APP))
    page.query_params.update({"enter": "1", "page": "validation", "lang": "ko"})
    page.run(timeout=30)
    assert_current_page(page, "validation")
    # Synthetic user-defined criteria exercise editable rules and both bounds;
    # these numbers are test fixtures, not proposed regulatory acceptance limits.
    page.session_state["vcc_ext_editor_assay"] = {
        "edited_rows": {0: {
            app_module.COLUMN_KO["Rule"]: "between",
            app_module.COLUMN_KO["Result"]: 0.45,
            app_module.COLUMN_KO["Lower"]: 0.5,
            app_module.COLUMN_KO["Upper"]: 0.9,
        }}, "added_rows": [], "deleted_rows": [],
    }
    page.session_state["q14_editor_assay"] = {
        "edited_rows": {0: {app_module.COLUMN_KO["Status"]: app_module.localize_value("Defined", "ko")}},
        "added_rows": [], "deleted_rows": [],
    }
    page.run(timeout=30)
    assert_no_exception(page)
    criteria = page.session_state["validation_ext_tables"]["assay"].copy(deep=True)
    q14 = page.session_state["q14_development_tables"]["assay"].copy(deep=True)
    first = criteria.iloc[0]
    if (first["Rule"], first["Lower"], first["Upper"], first["Result"]) != ("between", 0.5, 0.9, 0.45):
        raise AssertionError("Edited validation criteria did not reach the saved review table")
    if app_module.evaluate_rule(first) != "Review":
        raise AssertionError("The user-defined rule did not change the review result")
    if q14.iloc[0]["Status"] != "Defined" or evaluate_q14_problem(q14.iloc[0]) != "Pass":
        raise AssertionError("The Q14 status edit did not change its review result")

    page.button(key="workflow_response").click().run(timeout=30)
    assert_current_page(page, "response")
    page.button(key="workflow_validation").click().run(timeout=30)
    assert_current_page(page, "validation")
    page.button(key="vcc_ext_related_substances").click().run(timeout=30)
    assert_no_exception(page)
    page.button(key="vcc_ext_assay").click().run(timeout=30)
    assert_no_exception(page)
    pd.testing.assert_frame_equal(page.session_state["validation_ext_tables"]["assay"], criteria, obj="Edited assay acceptance criteria")
    pd.testing.assert_frame_equal(page.session_state["q14_development_tables"]["assay"], q14, obj="Edited Q14 development status")


def assert_q3d_scope_and_pde_edits_survive_navigation() -> None:
    page = AppTest.from_file(str(APP))
    page.query_params.update({"enter": "1", "page": "validation", "lang": "ko"})
    page.session_state["validation_test_item"] = "elemental_impurities"
    page.run(timeout=30)
    assert_current_page(page, "validation")
    page.radio(key="q3d_scope_mode").set_value("Full Q3D 24 elements").run(timeout=30)
    page.selectbox(key="q3d_route").set_value("Parenteral").run(timeout=30)
    page.number_input(key="q3d_daily_intake_g_day").set_value(4.0).run(timeout=30)
    assert_no_exception(page)
    if int(page.session_state["q3d_element_df"]["Include"].sum()) != 24:
        raise AssertionError("Full Q3D selection did not activate all 24 elements")
    page.session_state["q3d_element_editor"] = {
        "edited_rows": {0: {"Route PDE entered (ug/day)": 12.0, "Precision RSD (%)": 22.0}},
        "added_rows": [], "deleted_rows": [],
    }
    page.run(timeout=30)
    assert_no_exception(page)
    elements = page.session_state["q3d_element_df"].copy(deep=True)
    if elements.iloc[0]["Route PDE entered (ug/day)"] != 12.0 or elements.iloc[0]["Precision RSD (%)"] != 22.0:
        raise AssertionError("Product-specific elemental impurity edits were not saved")
    page.button(key="workflow_dashboard").click().run(timeout=30)
    assert_current_page(page, "dashboard")
    page.button(key="workflow_validation").click().run(timeout=30)
    assert_current_page(page, "validation")
    page.button(key="vcc_ext_assay").click().run(timeout=30)
    assert_no_exception(page)
    page.button(key="vcc_ext_elemental_impurities").click().run(timeout=30)
    assert_no_exception(page)
    if page.radio(key="q3d_scope_mode").value != "Full Q3D 24 elements" or page.selectbox(key="q3d_route").value != "Parenteral":
        raise AssertionError("Q3D scope or administration route reset during navigation")
    if page.number_input(key="q3d_daily_intake_g_day").value != 4.0:
        raise AssertionError("The Q3D daily intake reset during navigation")
    pd.testing.assert_frame_equal(page.session_state["q3d_element_df"], elements, obj="Product-specific Q3D edits")


def assert_related_pde_calculation_and_application_survive_navigation() -> None:
    page = AppTest.from_file(str(APP))
    page.query_params.update({"enter": "1", "page": "validation", "lang": "ko"})
    page.session_state["validation_test_item"] = "related_substances"
    page.run(timeout=30)
    assert_current_page(page, "validation")
    entries = {"related_mdd_mg_day": 125.0, "related_impurity_pde_ug_day": 50.0, "related_sample_conc_mg_ml": 0.8}
    for key, value in entries.items():
        page.number_input(key=key).set_value(value).run(timeout=30)
        assert_no_exception(page)
    frame = page.session_state["related_pde_frame"].copy(deep=True)
    target = frame[frame["Threshold"] == "Validation target"].iloc[0]
    if abs(float(target["Limit (%)"]) - 0.04) > 1e-9 or abs(float(target["Method concentration (ug/mL)"]) - 0.32) > 1e-9:
        raise AssertionError("Edited PDE/TDI inputs did not produce the expected concentration fixture")
    page.button(key="apply_related_pde_ref").click().run(timeout=30)
    assert_no_exception(page)
    if abs(page.number_input(key="ext_prep_related_substances_ref").value - 0.32) > 1e-9:
        raise AssertionError("Applying the PDE calculation did not update sample preparation")
    calculation = dict(page.session_state["last_calc"])
    page.button(key="workflow_response").click().run(timeout=30)
    assert_current_page(page, "response")
    page.button(key="workflow_validation").click().run(timeout=30)
    assert_current_page(page, "validation")
    page.button(key="vcc_ext_assay").click().run(timeout=30)
    assert_no_exception(page)
    page.button(key="vcc_ext_related_substances").click().run(timeout=30)
    assert_no_exception(page)
    for key, value in entries.items():
        if page.number_input(key=key).value != value:
            raise AssertionError(f"Related-substance input {key} reset during navigation")
    if page.session_state["last_calc"] != calculation:
        raise AssertionError("The applied PDE reference or sample preparation result reset")
    pd.testing.assert_frame_equal(page.session_state["related_pde_frame"], frame, obj="Edited PDE/TDI calculation")


def run_page(page_key: str, expected_text: list[str]) -> str:
    page = AppTest.from_file(str(APP))
    page.session_state["entered_app"] = True
    page.query_params["page"] = page_key
    page.query_params["lang"] = "ko"
    page.run(timeout=30)
    assert_current_page(page, page_key)
    text = collect_visible_text(page)
    missing = [label for label in expected_text if label not in text]
    if missing:
        raise AssertionError(f"{page_key} page is missing expected items: {missing}")
    return text


def assert_localization_schema_and_extension_idempotency() -> None:
    import app as app_module
    from validation_extension import apply_validation_extension

    # Localized editable headers must restore the exact original schema.
    # "Evidence required" used to become "Evidence needed", causing the
    # memo to crash after users visited the Korean document workspace.
    original = pd.DataFrame({column: [f"Custom value for {column}"] for column in app_module.COLUMN_KO})
    restored = app_module.delocalize_dataframe(app_module.localize_dataframe(original, "ko"), "ko")
    pd.testing.assert_frame_equal(restored, original, obj="Localized editable schema roundtrip")

    apply_validation_extension(app_module)
    names = ("initialize_state", "response_rows", "build_decision_packet")
    installed = {name: getattr(app_module, name) for name in names}
    apply_validation_extension(app_module)
    for name, function in installed.items():
        if getattr(app_module, name) is not function:
            raise AssertionError(f"Repeated extension initialization wrapped {name} again")


def assert_body_translation() -> None:
    import app as app_module

    profile = {
        "active_substance": "Naltrexone",
        "api_supplier": "API supplier / DMF holder to confirm",
        "formulation_platform": "PLGA long-acting microsphere",
        "clinical_material": "Clinical batch genealogy to confirm",
        "target_regions": "US / Korea / EU strategy to confirm",
    }
    checks = {
        "document logic": app_module.localize_dataframe(pd.DataFrame(app_module.default_document_logic_rows()), "ko"),
        "profile prompts": app_module.localize_dataframe(app_module.product_profile_prompts(profile), "ko"),
        "evidence map": app_module.localize_dataframe(pd.DataFrame(app_module.default_evidence_rows()), "ko"),
        "spec rationale": app_module.localize_dataframe(pd.DataFrame(app_module.default_spec_rows()), "ko"),
        "dmf bridge": app_module.localize_dataframe(pd.DataFrame(app_module.default_dmf_rows()), "ko"),
    }
    expected = {
        "document logic": ["API 패키지가 완제 조성", "근거 없는 기준이나 계산 오류"],
        "profile prompts": ["임상시험용 의약품에 사용된 API", "현재 DMF 버전과 공급자 commitment"],
        "evidence map": ["API 동일성, 명칭, 구조", "P.5.6 설정 근거"],
        "spec rationale": ["함량 기준이 API 역가", "무균보증 전략"],
        "dmf bridge": ["현재 DMF 버전과 holder", "완제 CQA 및 시험방법 관리"],
    }
    for label, frame in checks.items():
        text = frame.to_string()
        missing = [item for item in expected[label] if item not in text]
        if missing:
            raise AssertionError(f"{label} Korean body translation missing: {missing}")


def main() -> None:
    assert_localization_schema_and_extension_idempotency()
    test = assert_landing_and_entry()
    assert_navigation_and_session_persistence(test)
    assert_calculation_inputs_survive_navigation()
    assert_edited_validation_criteria_and_q14_survive_navigation()
    assert_q3d_scope_and_pde_edits_survive_navigation()
    assert_related_pde_calculation_and_application_survive_navigation()

    page_checks = {
        "intake": ["고객 CTD 문서 접수", "문서 접수", "고객 질문", "CTD 업데이트"],
        "documents": ["원문·확인값 입력", "문서 적용 로직", "핵심 판단 포인트", "문서 입력값을 근거 맵에 적용", "DMF 원문 입력", "CTD 3.2.S 원료의약품 입력", "CTD 3.2.P 완제의약품 입력"],
        "dashboard": ["문서 접수 준비도", "CTD 문서 준비도", "판단 배경", "핵심 판단 포인트"],
        "evidence": ["CTD 근거 맵", "제품 프로필 기반 검토 질문", "고위험 CTD 항목"],
        "spec": ["규격 설정 근거 (P.5.6)", "심사 리스크 집중 검토"],
        "dmf": ["원료·완제 연결성"],
        "validation": ["계산·밸리데이션 검토", "시험항목별 밸리데이션 선택"],
        "response": ["검토 메모", "검토 메모 미리보기", "Markdown 미리보기", "API 패키지가 완제 조성"],
        "launcher": ["연결 도구", "Clinical Trial Intelligence", "ToxiGuard-SOP Gate", "ToxiGuard-MediLens"],
    }
    for page_key, expected in page_checks.items():
        run_page(page_key, expected)
    assert_body_translation()

    validation_page = AppTest.from_file(str(APP))
    validation_page.session_state["entered_app"] = True
    validation_page.session_state["validation_test_item"] = "elemental_impurities"
    validation_page.query_params["page"] = "validation"
    validation_page.query_params["lang"] = "ko"
    validation_page.run(timeout=30)
    if validation_page.exception:
        raise AssertionError(validation_page.exception)
    validation_blocks = [getattr(item, "value", "") for item in validation_page.markdown]
    validation_blocks += [getattr(item, "value", "") for item in validation_page.info]
    validation_blocks += [getattr(item, "value", "") for item in validation_page.warning]
    validation_blocks += [getattr(item, "label", "") for item in validation_page.selectbox]
    validation_blocks += [getattr(item, "label", "") for item in validation_page.number_input]
    validation_markdown = "\n".join(validation_blocks)
    if validation_page.selectbox(key="detail_page_widget").value != "validation":
        raise AssertionError("The validation URL did not synchronize the native page selector")
    expected_validation_items = [
        "함량",
        "유연물질",
        "용출",
        "금속불순물",
        "니트로사민",
        "ICH M14",
        "ICH Q14 분석법 설정 문제점",
        "밸리데이션 결과만으로 충분하지 않습니다",
        "ICH Q3D 금속불순물 범위",
        "Q3D 실무 해석",
        "Full Q3D screening",
        "투여경로",
        "허용농도",
    ]
    missing_validation_items = [label for label in expected_validation_items if label not in validation_markdown]
    if missing_validation_items:
        raise AssertionError(f"Missing test-specific validation review items: {missing_validation_items}")

    related_page = AppTest.from_file(str(APP))
    related_page.session_state["entered_app"] = True
    related_page.session_state["validation_test_item"] = "related_substances"
    related_page.query_params["page"] = "validation"
    related_page.query_params["lang"] = "ko"
    related_page.run(timeout=30)
    if related_page.exception:
        raise AssertionError(related_page.exception)
    related_blocks = [getattr(item, "value", "") for item in related_page.markdown]
    related_blocks += [getattr(item, "value", "") for item in related_page.info]
    related_blocks += [getattr(item, "label", "") for item in related_page.button]
    related_blocks += [getattr(item, "label", "") for item in related_page.number_input]
    related_text = "\n".join(related_blocks)
    expected_related_items = [
        "유연물질 PDE/TDI 기준량",
        "ICH Q3B(R2)",
        "밸리데이션 target",
        "계산된 기준농도를 시료 제조에 적용",
    ]
    missing_related_items = [label for label in expected_related_items if label not in related_text]
    if missing_related_items:
        raise AssertionError(f"Missing related-substance PDE review items: {missing_related_items}")

    print("ToxiGuard Platform Ver.3 validation passed")


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT))
    main()

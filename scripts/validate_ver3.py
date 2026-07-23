from __future__ import annotations

from pathlib import Path
import sys

from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "streamlit_app.py"


def collect_visible_text(page: AppTest) -> str:
    blocks: list[str] = []
    for collection_name in [
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
    ]:
        collection = getattr(page, collection_name, [])
        blocks += [getattr(item, "value", "") for item in collection]
        blocks += [getattr(item, "label", "") for item in collection]
    return "\n".join(str(block) for block in blocks if block)


def run_page(page_key: str, expected_text: list[str]) -> str:
    page = AppTest.from_file(str(APP))
    page.session_state["entered_app"] = True
    page.query_params["page"] = page_key
    page.run(timeout=30)
    if page.exception:
        raise AssertionError(page.exception)
    text = collect_visible_text(page)
    missing = [label for label in expected_text if label not in text]
    if missing:
        raise AssertionError(f"{page_key} page is missing expected items: {missing}")
    return text


def main() -> None:
    landing = AppTest.from_file(str(APP))
    landing.run(timeout=30)
    if landing.exception:
        raise AssertionError(landing.exception)
    if not landing.button or landing.button[0].label not in {"워크벤치 시작", "Enter Workbench"}:
        raise AssertionError("Landing entry button did not render")

    test = AppTest.from_file(str(APP))
    test.session_state["entered_app"] = True
    test.run(timeout=30)
    if test.exception:
        raise AssertionError(test.exception)
    expected_nav = [
        "고객 CTD 문서 접수",
        "00 문서 입력",
        "대시보드",
        "01 근거 맵",
        "02 P.5.6 기준 설정 근거",
        "03 DMF-완제 연결성",
        "04 계산 / 밸리데이션",
        "05 RA 답변 메모",
        "앱 실행",
    ]

    markdown_values = [getattr(item, "value", "") for item in test.markdown]
    nav_markup = "\n".join(markdown_values)
    if "tg-icon-nav" not in nav_markup:
        raise AssertionError("Icon navigation did not render")
    missing = [label for label in expected_nav if label not in nav_markup]
    if missing:
        raise AssertionError(f"Missing icon navigation items: {missing}")

    if not any("ToxiGuard-VCC" in value for value in markdown_values):
        raise AssertionError("App header did not render")
    if "고객 미팅 요약" not in nav_markup and "Client Meeting Summary" not in nav_markup:
        raise AssertionError("Client CTD Intake default page did not render")

    page_checks = {
        "intake": ["고객 CTD 문서 접수", "문서 접수", "고객 질문", "CTD 업데이트"],
        "documents": ["00 문서 입력", "문서 적용 로직", "핵심 판단 포인트", "문서 입력값을 근거 맵에 적용", "DMF 원문 입력", "CTD 3.2.S 원료의약품 입력", "CTD 3.2.P 완제의약품 입력"],
        "dashboard": ["대시보드", "문서 접수 준비도", "CTD 문서 준비도", "판단 배경", "핵심 판단 포인트"],
        "evidence": ["01 근거 맵", "제품 프로필 기반 검토 질문", "고위험 CTD 항목"],
        "spec": ["02 P.5.6 기준 설정 근거", "심사 리스크 집중 검토"],
        "dmf": ["03 DMF-완제 연결성"],
        "validation": ["04 계산 / 밸리데이션", "시험항목별 밸리데이션 선택"],
        "response": ["05 RA 답변 메모", "CMC RA Decision Packet 미리보기", "Markdown 미리보기"],
        "launcher": ["앱 실행", "Clinical Trial Intelligence", "ToxiGuard-SOP Gate", "ToxiGuard-MediLens"],
    }
    for page_key, expected in page_checks.items():
        run_page(page_key, expected)

    validation_page = AppTest.from_file(str(APP))
    validation_page.session_state["entered_app"] = True
    validation_page.session_state["validation_test_item"] = "elemental_impurities"
    validation_page.query_params["page"] = "validation"
    validation_page.run(timeout=30)
    if validation_page.exception:
        raise AssertionError(validation_page.exception)
    validation_blocks = [getattr(item, "value", "") for item in validation_page.markdown]
    validation_blocks += [getattr(item, "value", "") for item in validation_page.info]
    validation_blocks += [getattr(item, "value", "") for item in validation_page.warning]
    validation_blocks += [getattr(item, "label", "") for item in validation_page.selectbox]
    validation_blocks += [getattr(item, "label", "") for item in validation_page.number_input]
    validation_markdown = "\n".join(validation_blocks)
    if 'aria-current="page"' not in validation_markdown or "04 계산 / 밸리데이션" not in validation_markdown:
        raise AssertionError("Icon navigation did not open the validation page")
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

"""Local integration regressions for document receipt and request tracking.

All uploads are synthetic test fixtures. AppTest drives the actual upload,
navigation, and submit widgets; the review model and callbacks are not mocked.
Run from any working directory:
    python3 work/vcc/scripts/validate_document_upload_ui.py
"""
from __future__ import annotations

import copy
from datetime import date
from pathlib import Path
import sys
import traceback

import pandas as pd
from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
APP = ROOT / "streamlit_app.py"

from document_intake import SECTION_CATALOG, request_rows, section_status, summary_rows
from document_intake_ui import STATE_KEY


SOURCE_SECTION = "DMF.ADMIN"
OTHER_SECTION = "CTD.3.2.P.5"
# Deliberately collide with built-in Korean translations. Customer filenames
# and request wording must remain verbatim when the surrounding memo localizes.
FIXTURE_NAME = "Manufacturing process.txt"
FIXTURE_BYTES = "Synthetic upload fixture only.\nNo verified evidence or analytical result.\n".encode("utf-8")
FRAME_KEYS = ("intake_df", "evidence_df", "spec_df", "dmf_df", "dmf_source_df",
              "ctd_document_df", "document_logic_df", "validation_df")
REQUEST_NOTE = "Request source text and confirmed values for API identity, grade, specification, impurity, and retest controls."
REQUEST_OWNER = "Fixture CMC reviewer"
REQUEST_DUE = date(2030, 1, 15)


def clean_run(page: AppTest) -> AppTest:
    page.run(timeout=30)
    assert not page.exception, [(error.message, error.stack_trace) for error in page.exception]
    return page


def start() -> AppTest:
    page = AppTest.from_file(str(APP), default_timeout=30)
    page.query_params.update({"enter": "1", "page": "documents", "lang": "ko"})
    return clean_run(page)


def go_to(page: AppTest, destination: str) -> None:
    page.selectbox(key="detail_page_widget").set_value(destination)
    clean_run(page)
    assert page.session_state["active_page"] == destination


def preserve_workbench(page: AppTest):
    return ({key: page.session_state[key].copy(deep=True) for key in FRAME_KEYS},
            copy.deepcopy(page.session_state["profile_values"]))


def assert_workbench_unchanged(page: AppTest, saved) -> None:
    frames, profile = saved
    assert page.session_state["profile_values"] == profile
    for key, frame in frames.items():
        pd.testing.assert_frame_equal(page.session_state[key], frame,
                                      obj=f"Unrelated review workbench {key}")


def registry(page: AppTest) -> dict:
    return page.session_state[STATE_KEY]


def submit(page: AppTest, label: str) -> None:
    matches = [button for button in page.button if button.label == label]
    assert len(matches) == 1, f"Expected one submit button {label!r}, found {len(matches)}"
    matches[0].click()
    clean_run(page)


def assert_missing_count(page: AppTest, count: int) -> None:
    lang = page.session_state["lang"]
    label = "정보없는 섹션" if lang == "ko" else "Sections without information"
    metrics = [metric for metric in page.metric if metric.label == label]
    assert len(metrics) == 1
    assert int(metrics[0].value) == count
    actual = sum(not row["file_count"] and row["status"] != "해당없음"
                 for row in summary_rows(registry(page)))
    assert actual == count


def upload(page: AppTest, *, extras=(), contents=None) -> str:
    if contents is None:
        contents = [(FIXTURE_NAME, FIXTURE_BYTES, "text/plain")]
    page.file_uploader(key=f"doc_intake_upload_{SOURCE_SECTION}").set_value(contents)
    page.multiselect(key=f"doc_intake_extra_{SOURCE_SECTION}").set_value(list(extras))
    submit(page, "선택 섹션에 파일 등록")
    assert not page.error, [error.value for error in page.error]
    assert len(registry(page)["files"]) == 1
    return next(iter(registry(page)["files"]))


def save_request(page: AppTest, *, section=SOURCE_SECTION, status="추가자료요청",
                 note=REQUEST_NOTE) -> None:
    page.selectbox(key="doc_intake_request_section").set_value(section)
    clean_run(page)
    lang = page.session_state["lang"]
    suffix = f"{section}_{lang}"
    page.selectbox(key=f"doc_intake_status_{suffix}").set_value(status)
    page.text_area(key=f"doc_intake_note_{suffix}").set_value(note)
    page.text_input(key=f"doc_intake_owner_{suffix}").set_value(REQUEST_OWNER)
    page.date_input(key=f"doc_intake_due_{suffix}").set_value(REQUEST_DUE)
    page.selectbox(key=f"doc_intake_priority_{suffix}").set_value("높음")
    submit(page, "요청 내용 저장" if lang == "ko" else "Save information request")
    assert not page.error, [error.value for error in page.error]


def assert_initial_receipt_is_separate_from_example_data() -> None:
    page = start()
    state = registry(page)
    assert len(SECTION_CATALOG) == 27
    assert len(state["section_states"]) == 27
    assert state["files"] == {}
    rows = summary_rows(state)
    assert len(rows) == 27
    assert {row["status"] for row in rows} == {"정보없음"}
    assert all(row["file_count"] == 0 and not row["file_names"] for row in rows)
    assert all(not row[field] for row in rows for field in ("request", "owner", "due_date"))
    assert len(request_rows(state)) == 27
    assert_missing_count(page, 27)
    assert page.session_state["profile_values"]["active_substance"] == "Naltrexone"
    inventory = [table.value for table in page.dataframe if "검토 상태" in table.value.columns]
    assert len(inventory) == 1 and len(inventory[0]) == 27
    assert set(inventory[0]["접수 현황"]) == {"정보없음"}
    assert set(inventory[0]["검토 상태"]) == {"정보없음"}


def assert_explicit_upload_and_workbench_isolation() -> None:
    page = start()
    saved = preserve_workbench(page)
    page.file_uploader(key=f"doc_intake_upload_{SOURCE_SECTION}").set_value(
        (FIXTURE_NAME, FIXTURE_BYTES, "text/plain"))
    clean_run(page)
    assert registry(page)["files"] == {}, "Selecting a file must not register it before submission"
    file_id = upload(page, extras=[OTHER_SECTION])
    record = registry(page)["files"][file_id]
    assert record["content"] == FIXTURE_BYTES
    assert record["name"] == FIXTURE_NAME
    assert set(record["section_ids"]) == {SOURCE_SECTION, OTHER_SECTION}
    assert record["size"] == len(FIXTURE_BYTES)
    assert section_status(registry(page), SOURCE_SECTION) == "검토대기"
    assert section_status(registry(page), OTHER_SECTION) == "검토대기"
    assert_missing_count(page, 25)
    assert len(request_rows(registry(page))) == 25
    assert_workbench_unchanged(page, saved)


def assert_request_owner_due_date_and_nonapplicability() -> None:
    page = start()
    upload(page)
    saved = preserve_workbench(page)
    save_request(page)
    state = registry(page)
    decision = state["section_states"][SOURCE_SECTION]
    assert decision == {"status": "추가자료요청", "note": REQUEST_NOTE,
                        "owner": REQUEST_OWNER, "due_date": REQUEST_DUE.isoformat(), "priority": "높음"}
    request = next(row for row in request_rows(state) if row["section_id"] == SOURCE_SECTION)
    assert request["request"] == REQUEST_NOTE and request["file_count"] == 1
    assert len(request_rows(state)) == 27
    assert_missing_count(page, 26)
    save_request(page, section=OTHER_SECTION, status="해당없음",
                 note="Synthetic fixture: this section does not apply to the review scope.")
    assert section_status(registry(page), OTHER_SECTION) == "해당없음"
    assert OTHER_SECTION not in {row["section_id"] for row in request_rows(registry(page))}
    assert_missing_count(page, 25)
    assert_workbench_unchanged(page, saved)


def assert_reclassification_and_removal_recalculate_missing() -> None:
    page = start()
    saved = preserve_workbench(page)
    file_id = upload(page, extras=[OTHER_SECTION])
    page.multiselect(key=f"doc_intake_reassign_{file_id}").set_value([OTHER_SECTION])
    submit(page, "섹션 연결 저장")
    state = registry(page)
    assert state["files"][file_id]["section_ids"] == [OTHER_SECTION]
    assert state["files"][file_id]["content"] == FIXTURE_BYTES
    assert section_status(state, SOURCE_SECTION) == "정보없음"
    assert section_status(state, OTHER_SECTION) == "검토대기"
    assert_missing_count(page, 26)
    assert len(request_rows(state)) == 26
    page.button(key=f"doc_intake_remove_{file_id}").click()
    clean_run(page)
    assert registry(page)["files"] == {}
    assert section_status(registry(page), OTHER_SECTION) == "정보없음"
    assert_missing_count(page, 27)
    assert len(request_rows(registry(page))) == 27
    assert_workbench_unchanged(page, saved)


def assert_navigation_preserves_bytes_and_response_memo() -> None:
    import app
    assert "Manufacturing process" in app.CONTENT_KO
    assert REQUEST_NOTE in app.CONTENT_KO, "Fixture must exercise a built-in translation collision"
    page = start()
    file_id = upload(page, extras=[OTHER_SECTION])
    save_request(page)
    saved_registry = copy.deepcopy(registry(page))
    saved_workbench = preserve_workbench(page)
    for lang, destination in (("en", "intake"), ("en", "validation"),
                              ("ko", "documents"), ("ko", "response")):
        page.radio(key="language_choice").set_value(lang)
        clean_run(page)
        go_to(page, destination)
        assert registry(page) == saved_registry
        assert registry(page)["files"][file_id]["content"] == FIXTURE_BYTES
        assert_workbench_unchanged(page, saved_workbench)
    memo = [area.value for area in page.text_area if "고객 파일 접수 현황" in area.value]
    assert len(memo) == 1, "The review memo must contain the actual receipt inventory"
    for expected in (FIXTURE_NAME, "누락·추가자료 요청", REQUEST_NOTE, REQUEST_OWNER, REQUEST_DUE.isoformat()):
        assert expected in memo[0], f"Missing receipt/request detail from review memo: {expected}"
    assert f"| {FIXTURE_NAME} |" in memo[0], "Korean memo must preserve the original customer filename"
    assert f"| {REQUEST_NOTE} |" in memo[0], "Korean memo must preserve the original customer request"
    assert "제조공정.txt" not in memo[0], "Customer filenames must never be translated"
    assert "doc_intake_request_section" not in [box.key for box in page.selectbox], "Response requests should be read-only"
    request_tables = [table.value for table in page.dataframe if "요청 내용" in table.value.columns]
    assert len(request_tables) == 1
    assert REQUEST_NOTE in request_tables[0]["요청 내용"].tolist()
    go_to(page, "documents")
    assert registry(page) == saved_registry
    assert_missing_count(page, 25)


def assert_failed_upload_batch_leaves_registry_unchanged() -> None:
    page = start()
    saved_registry = copy.deepcopy(registry(page))
    saved_workbench = preserve_workbench(page)
    page.file_uploader(key=f"doc_intake_upload_{SOURCE_SECTION}").set_value([
        (FIXTURE_NAME, FIXTURE_BYTES, "text/plain"),
        ("wrong-content.pdf", b"This fixture is not a PDF.", "application/pdf"),
    ])
    submit(page, "선택 섹션에 파일 등록")
    assert page.error, "Invalid file content should explain the rejected registration"
    assert registry(page) == saved_registry, "Failed batch must not retain a partially registered valid file"
    assert_missing_count(page, 27)
    assert_workbench_unchanged(page, saved_workbench)


def main() -> int:
    tests = [assert_initial_receipt_is_separate_from_example_data,
             assert_explicit_upload_and_workbench_isolation,
             assert_request_owner_due_date_and_nonapplicability,
             assert_reclassification_and_removal_recalculate_missing,
             assert_navigation_preserves_bytes_and_response_memo,
             assert_failed_upload_batch_leaves_registry_unchanged]
    failures = []
    for test in tests:
        try:
            test()
        except Exception:
            failures.append(test.__name__)
            print(f"FAIL {test.__name__}")
            traceback.print_exc()
        else:
            print(f"PASS {test.__name__}")
    print(f"Document upload UI validation: {len(tests) - len(failures)}/{len(tests)} groups passed")
    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(main())

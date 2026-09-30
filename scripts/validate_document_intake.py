"""Regressions for the isolated DMF/CTD document-intake model.

Run from any working directory with the Python standard library only:
    python3 work/vcc/scripts/validate_document_intake.py

These synthetic documents test receipt tracking, not document validity,
scientific evidence, or regulatory approval.
"""
from __future__ import annotations

import copy
import csv
import hashlib
import io
import json
from pathlib import Path
import sys
import unittest
import zipfile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import document_intake as intake


PDF = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF"
OLE = bytes.fromhex("D0 CF 11 E0 A1 B1 1A E1") + b" " * 504
S1 = "DMF.S.1"
S2 = "DMF.S.2"
CTD_S1 = "CTD.3.2.S.1"
ROW_KEYS = {
    "section_id", "group", "code", "label_ko", "label_en", "status",
    "file_count", "file_names", "request", "owner", "due_date", "priority",
}


def ooxml(part: str, *, content_types: bool = True) -> bytes:
    result = io.BytesIO()
    with zipfile.ZipFile(result, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        if content_types:
            archive.writestr("[Content_Types].xml", "<Types/>")
        archive.writestr(part, "<synthetic/>")
    return result.getvalue()


def sized_pdf(size: int, marker: bytes = b"x") -> bytes:
    prefix = b"%PDF-1.4\n" + marker + b"\n"
    suffix = b"\n%%EOF"
    return prefix + b" " * (size - len(prefix) - len(suffix)) + suffix


def all_keys(value):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from all_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from all_keys(child)


class IntakeModelTests(unittest.TestCase):
    def assert_rejected_without_mutation(self, operation, state, *args, **kwargs):
        before = copy.deepcopy(state)
        with self.assertRaises((ValueError, TypeError)):
            operation(state, *args, **kwargs)
        self.assertEqual(state, before)

    def upload(self, state=None, *, name="supplier.pdf", content=PDF, sections=(S1,), mime=""):
        return intake.add_file(intake.new_intake() if state is None else state,
                               name, content, list(sections), content_type=mime)

    def row(self, state, section_id):
        return next(row for row in intake.summary_rows(state) if row["section_id"] == section_id)

    def test_catalog_covers_all_27_sections_once(self):
        expected = {"DMF.ADMIN", "CTD.1", "CTD.2", "CTD.4", "CTD.5"}
        expected.update(f"DMF.S.{number}" for number in range(1, 8))
        expected.update(f"CTD.3.2.S.{number}" for number in range(1, 8))
        expected.update(f"CTD.3.2.P.{number}" for number in range(1, 9))
        self.assertIsInstance(intake.SECTION_CATALOG, tuple)
        self.assertEqual(len(intake.SECTION_CATALOG), 27)
        self.assertEqual({row["id"] for row in intake.SECTION_CATALOG}, expected)
        for row in intake.SECTION_CATALOG:
            for key in ("id", "group", "code", "label_ko", "label_en"):
                self.assertIsInstance(row[key], str)
                self.assertTrue(row[key].strip())

    def test_empty_intake_has_no_claims_or_legacy_evidence_state(self):
        state = intake.new_intake()
        self.assertEqual(set(state), {"schema_version", "files", "section_states"})
        self.assertEqual(state["schema_version"], 1)
        self.assertEqual(state["files"], {})
        rows = intake.summary_rows(state)
        self.assertEqual(len(rows), 27)
        for row in rows:
            self.assertEqual(set(row), ROW_KEYS)
            self.assertEqual(row["status"], "정보없음")
            self.assertEqual(row["file_count"], 0)
            self.assertEqual(intake.section_status(state, row["section_id"]), "정보없음")
        self.assertFalse({"evidence_df", "dmf_df", "ctd_document_df", "validation_df", "Ready", "Pass"}
                         .intersection(all_keys(state)))

    def test_upload_hash_metadata_and_review_pending(self):
        state = self.upload(mime="application/pdf")
        expected_id = hashlib.sha256(PDF).hexdigest()
        self.assertEqual(set(state["files"]), {expected_id})
        record = state["files"][expected_id]
        self.assertEqual(record["id"], expected_id)
        self.assertEqual(record["sha256"], expected_id)
        self.assertEqual(record["name"], "supplier.pdf")
        self.assertEqual(record["size"], len(PDF))
        self.assertEqual(record["content"], PDF)
        self.assertEqual(set(record["sections"]), {S1})
        self.assertEqual(record["section_ids"], record["sections"])
        self.assertEqual(record["content_type"], record["type"])
        self.assertEqual(intake.section_status(state, S1), "검토대기")
        self.assertEqual(self.row(state, S1)["file_count"], 1)
        self.assertIn("supplier.pdf", self.row(state, S1)["file_names"])

    def test_duplicate_content_unions_assignments_without_double_counting(self):
        state = self.upload()
        before = copy.deepcopy(state)
        updated = self.upload(state, name="renamed.pdf", sections=(S1, S2))
        self.assertEqual(state, before)
        self.assertEqual(len(updated["files"]), 1)
        record = next(iter(updated["files"].values()))
        self.assertEqual(set(record["sections"]), {S1, S2})
        self.assertEqual(record["section_ids"], record["sections"])
        self.assertEqual(self.row(updated, S1)["file_count"], 1)
        self.assertEqual(self.row(updated, S2)["file_count"], 1)

    def test_distinct_contents_are_distinct_files(self):
        state = self.upload()
        state = self.upload(state, name="supplier.pdf", content=PDF.replace(b"1 0 obj", b"2 0 obj"))
        self.assertEqual(len(state["files"]), 2)
        self.assertEqual(self.row(state, S1)["file_count"], 2)

    def test_assignment_does_not_claim_related_dmf_or_ctd_sections(self):
        state = self.upload(sections=(CTD_S1,))
        self.assertEqual(intake.section_status(state, CTD_S1), "검토대기")
        for section in (S1, "CTD.1", "CTD.2", "CTD.3.2.S.2", "CTD.3.2.P.1"):
            self.assertEqual(intake.section_status(state, section), "정보없음")
            self.assertEqual(self.row(state, section)["file_count"], 0)

    def test_reassignment_replaces_old_associations(self):
        state = self.upload(sections=(S1, S2))
        file_id = next(iter(state["files"]))
        before = copy.deepcopy(state)
        updated = intake.reassign_file(state, file_id, [CTD_S1])
        self.assertEqual(state, before)
        self.assertEqual(set(updated["files"][file_id]["sections"]), {CTD_S1})
        self.assertEqual(updated["files"][file_id]["section_ids"], [CTD_S1])
        for section in (S1, S2):
            self.assertEqual(intake.section_status(updated, section), "정보없음")
            self.assertEqual(self.row(updated, section)["file_count"], 0)
        self.assertEqual(intake.section_status(updated, CTD_S1), "검토대기")

    def test_delete_removes_file_from_every_section(self):
        state = self.upload(sections=(S1, S2))
        before = copy.deepcopy(state)
        updated = intake.delete_file(state, next(iter(state["files"])))
        self.assertEqual(state, before)
        self.assertFalse(updated["files"])
        for section in (S1, S2):
            self.assertEqual(intake.section_status(updated, section), "정보없음")
            self.assertEqual(self.row(updated, section)["file_count"], 0)

    def test_all_mutations_return_independent_state(self):
        empty = intake.new_intake()
        uploaded = self.upload(empty)
        file_id = next(iter(uploaded["files"]))
        operations = (
            lambda: intake.reassign_file(uploaded, file_id, [S2]),
            lambda: intake.delete_file(uploaded, file_id),
            lambda: intake.set_section_state(uploaded, S1, "추가자료요청", "Source needed"),
        )
        before = copy.deepcopy(uploaded)
        for operation in operations:
            with self.subTest(operation=operation):
                result = operation()
                self.assertIsNot(result, uploaded)
                result["section_states"]["test_mutation"] = {"note": "must stay isolated"}
                result["section_states"][S2]["note"] = "nested mutation must stay isolated"
                self.assertEqual(uploaded, before)
        uploaded["files"][file_id]["name"] = "changed.pdf"
        self.assertFalse(empty["files"])
        independent = intake.new_intake()
        self.assertFalse(independent["files"])
        self.assertNotIn("test_mutation", independent["section_states"])

    def test_explicit_request_and_not_applicable_survive_uploads(self):
        for status in ("추가자료요청", "해당없음"):
            with self.subTest(status=status):
                state = intake.set_section_state(intake.new_intake(), S1, status, "Supplier follow-up",
                                                  owner="Analytical team", due_date="2026-10-15", priority="높음")
                updated = self.upload(state)
                self.assertEqual(intake.section_status(updated, S1), status)
                row = self.row(updated, S1)
                self.assertEqual(row["request"], "Supplier follow-up")
                self.assertEqual(row["owner"], "Analytical team")
                self.assertEqual(row["due_date"], "2026-10-15")
                self.assertEqual(row["priority"], "높음")

    def test_explicit_request_survives_removing_last_file(self):
        state = self.upload()
        state = intake.set_section_state(state, S1, "추가자료요청", "Need signed replacement")
        updated = intake.delete_file(state, next(iter(state["files"])))
        self.assertEqual(intake.section_status(updated, S1), "추가자료요청")
        self.assertEqual(self.row(updated, S1)["request"], "Need signed replacement")

    def test_unsupported_claims_and_contradictory_states_are_rejected(self):
        empty = intake.new_intake()
        for status in ("Ready", "Pass", "approved", "Approved", "Complete", ""):
            with self.subTest(status=status):
                self.assert_rejected_without_mutation(intake.set_section_state, empty, S1, status)
        self.assert_rejected_without_mutation(intake.set_section_state, empty, S1, "검토대기")
        self.assert_rejected_without_mutation(intake.set_section_state, self.upload(), S1, "정보없음")

    def test_invalid_request_dates_and_priorities_are_rejected(self):
        state = intake.new_intake()
        for due_date in ("2026-02-30", "2026-1-01", "10/15/2026", "tomorrow", "20261015"):
            with self.subTest(due_date=due_date):
                self.assert_rejected_without_mutation(intake.set_section_state, state, S1,
                                                       "추가자료요청", due_date=due_date)
        for priority in ("urgent", "높음;Pass", ""):
            with self.subTest(priority=priority):
                self.assert_rejected_without_mutation(intake.set_section_state, state, S1,
                                                       "추가자료요청", priority=priority)

    def test_invalid_section_assignments_and_missing_file_ids_are_rejected(self):
        empty = intake.new_intake()
        self.assert_rejected_without_mutation(intake.add_file, empty, "supplier.pdf", PDF, ["CTD.99"])
        self.assert_rejected_without_mutation(intake.add_file, empty, "supplier.pdf", PDF, [])
        self.assert_rejected_without_mutation(intake.add_file, empty, "supplier.pdf", PDF, S1)
        self.assert_rejected_without_mutation(intake.set_section_state, empty, "CTD.99", "정보없음")
        uploaded = self.upload()
        file_id = next(iter(uploaded["files"]))
        self.assert_rejected_without_mutation(intake.reassign_file, uploaded, file_id, ["DMF.S.99"])
        self.assert_rejected_without_mutation(intake.reassign_file, uploaded, file_id, [])
        self.assert_rejected_without_mutation(intake.reassign_file, uploaded, "missing-file", [S2])
        self.assert_rejected_without_mutation(intake.delete_file, uploaded, "missing-file")

    def test_supported_formats_are_received_without_streamlit(self):
        cases = (
            ("sample.pdf", PDF, "application/pdf"),
            ("sample.docx", ooxml("word/document.xml"),
             "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
            ("sample.xlsx", ooxml("xl/workbook.xml"),
             "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
            ("sample.txt", "자료 수령 기록\n".encode("utf-8"), "text/plain"),
            ("sample.txt", "자료 수령 기록\n".encode("utf-16"), "text/plain"),
            ("sample.doc", OLE, "application/msword"),
            ("sample.xls", OLE, "application/vnd.ms-excel"),
        )
        for name, content, mime in cases:
            with self.subTest(name=name, mime=mime, size=len(content)):
                state = self.upload(name=name, content=content, mime=mime)
                self.assertEqual(len(state["files"]), 1)
                self.assertEqual(intake.section_status(state, S1), "검토대기")

    def test_empty_unsupported_mime_and_signature_mismatches_are_rejected(self):
        invalid = (
            ("empty.pdf", b"", "application/pdf"),
            ("sample.exe", PDF, "application/pdf"),
            ("no_extension", PDF, "application/pdf"),
            ("sample.pdf", PDF, "image/png"),
            ("sample.pdf", b"This is not a PDF", "application/pdf"),
            ("sample.doc", b"fake legacy Office", "application/msword"),
            ("sample.xls", b"fake legacy Office", "application/vnd.ms-excel"),
            ("sample.doc", OLE[:8], "application/msword"),
            ("sample.docx", b"PK-not-a-zip", ""),
            ("sample.docx", ooxml("xl/workbook.xml"), ""),
            ("sample.xlsx", ooxml("word/document.xml"), ""),
            ("sample.docx", ooxml("word/document.xml", content_types=False), ""),
            ("sample.txt", b"binary\x00payload", "text/plain"),
            ("sample.txt", b"\xff\xfe\x00\x00", "text/plain"),
            ("sample.txt", b"\xff\x80\x81", "text/plain"),
        )
        for name, content, mime in invalid:
            with self.subTest(name=name, content=content[:30], mime=mime):
                self.assert_rejected_without_mutation(intake.add_file, intake.new_intake(),
                                                       name, content, [S1], content_type=mime)

    def test_filename_sanitization_keeps_basename_and_extension(self):
        for name in ("../../supplier.pdf", r"C:\private\supplier.pdf", r"..\..\supplier.pdf"):
            with self.subTest(name=name):
                state = self.upload(name=name)
                stored = next(iter(state["files"].values()))["name"]
                self.assertEqual(stored, "supplier.pdf")
        sanitized = intake.safe_filename("supply\x00\x1f\x7f\nreport.pdf")
        self.assertTrue(sanitized.endswith(".pdf"))
        self.assertFalse(any(ord(char) < 32 or ord(char) == 127 for char in sanitized))
        long_name = "자료" * 2000 + ".pdf"
        shortened = intake.safe_filename(long_name)
        self.assertLess(len(shortened), len(long_name))
        self.assertTrue(shortened.endswith(".pdf"))

    def test_windows_reserved_names_and_characters_are_portable(self):
        for name in ("CON.pdf", "prn.txt", "AUX.doc", "NUL.xls", "com1.docx", "LPT9.xlsx"):
            with self.subTest(name=name):
                sanitized = intake.safe_filename(name)
                self.assertEqual(sanitized, "_" + name)
        sanitized = intake.safe_filename('supplier<draft>:version"2|final?*.pdf')
        self.assertTrue(sanitized.endswith(".pdf"))
        self.assertFalse(set('<>:"|?*').intersection(sanitized))

    def test_per_file_limit_rejects_more_than_20_mib(self):
        self.assertEqual(intake.MAX_FILE_BYTES, 20 * 1024 * 1024)
        oversized = sized_pdf(intake.MAX_FILE_BYTES + 1)
        self.assert_rejected_without_mutation(intake.add_file, intake.new_intake(),
                                               "oversized.pdf", oversized, [S1])

    def test_total_content_limit_is_100_mib_and_dedup_does_not_consume_it_again(self):
        state = intake.new_intake()
        for index in range(5):
            content = sized_pdf(20 * 1024 * 1024, str(index).encode("ascii"))
            state = self.upload(state, name=f"part-{index}.pdf", content=content)
        self.assertEqual(sum(record["size"] for record in state["files"].values()), 100 * 1024 * 1024)
        before = copy.deepcopy(state)
        duplicate = self.upload(state, name="duplicate.pdf", content=content, sections=(S2,))
        self.assertEqual(len(duplicate["files"]), 5)
        self.assertEqual(state, before)
        self.assert_rejected_without_mutation(intake.add_file, state, "one-too-many.pdf", PDF, [S1])

    def test_50_file_limit_and_duplicate_at_capacity(self):
        state = intake.new_intake()
        for index in range(50):
            content = f"Synthetic intake file {index}".encode("utf-8")
            state = self.upload(state, name=f"file-{index}.txt", content=content)
        self.assertEqual(len(state["files"]), 50)
        duplicate = self.upload(state, name="copy.txt", content=content, sections=(S2,))
        self.assertEqual(len(duplicate["files"]), 50)
        self.assert_rejected_without_mutation(intake.add_file, state, "file-51.txt", b"Unique file 51", [S1])

    def test_requests_only_include_missing_and_explicit_follow_up_sections(self):
        state = self.upload(sections=(S1,))
        state = intake.set_section_state(state, S2, "해당없음", "Not in this project")
        state = intake.set_section_state(state, CTD_S1, "추가자료요청", "Obtain source record")
        for language in ("ko", "en"):
            with self.subTest(language=language):
                rows = intake.request_rows(state, lang=language)
                self.assertEqual(len(rows), 25)
                by_id = {row["section_id"]: row for row in rows}
                self.assertNotIn(S1, by_id)
                self.assertNotIn(S2, by_id)
                self.assertEqual(by_id[CTD_S1]["request"], "Obtain source record")
                for row in rows:
                    self.assertEqual(set(row), ROW_KEYS)
                    self.assertIn(row["status"], ("정보없음", "추가자료요청"))
                    self.assertTrue(row["request"].strip())

    def test_request_csv_is_utf8_bom_and_preserves_multiline_notes(self):
        note = '서명본 요청, 버전 확인\nSecond line with "quotes"'
        state = intake.set_section_state(intake.new_intake(), S1, "추가자료요청", note,
                                         owner="품질팀", due_date="2026-10-15", priority="보통")
        for language in ("ko", "en"):
            with self.subTest(language=language):
                payload = intake.request_csv(state, lang=language)
                self.assertIsInstance(payload, bytes)
                self.assertTrue(payload.startswith(b"\xef\xbb\xbf"))
                rows = list(csv.reader(io.StringIO(payload.decode("utf-8-sig"))))
                self.assertEqual(len(rows), len(intake.request_rows(state, lang=language)) + 1)
                self.assertTrue(all(len(row) == len(rows[0]) for row in rows))
                self.assertIn(note, [cell for row in rows[1:] for cell in row])
                self.assertIn("품질팀", [cell for row in rows[1:] for cell in row])

    def test_request_csv_separates_receipt_from_review_state_in_both_languages(self):
        state = self.upload(sections=(S2,))
        notes = {S1: "자료 원본을 제공해 주세요.", S2: "접수된 자료의 서명본을 추가해 주세요."}
        for section, note in notes.items():
            state = intake.set_section_state(state, section, "추가자료요청", note)
        before = copy.deepcopy(state)
        cases = (
            ("ko", "섹션 ID", "접수 상태", "검토 상태", "추가정보 요청",
             "정보없음", "파일 접수", "추가자료요청"),
            ("en", "Section ID", "Receipt status", "Review state", "Information request",
             "No information", "Files received", "Additional information requested"),
        )
        for language, id_column, receipt_column, review_column, note_column, missing, received, requested in cases:
            with self.subTest(language=language):
                payload = intake.request_csv(state, lang=language).decode("utf-8-sig")
                rows = {row[id_column]: row for row in csv.DictReader(io.StringIO(payload))}
                self.assertEqual(rows[S1][receipt_column], missing)
                self.assertEqual(rows[S2][receipt_column], received)
                for section, note in notes.items():
                    self.assertEqual(rows[section][review_column], requested)
                    self.assertEqual(rows[section][note_column], note)
                    self.assertEqual(intake.section_status(state, section), "추가자료요청")
                self.assertEqual(state, before)

    def test_csv_neutralizes_formula_injection_in_notes_names_and_owner(self):
        for prefix in ("=", "+", "-", "@"):
            with self.subTest(prefix=prefix):
                name = f"{prefix}SUM(1,1).txt"
                note = f'{prefix}HYPERLINK("https://example.invalid","open")'
                owner = prefix + "Responsible person"
                state = self.upload(name=name, content=b"Synthetic file")
                state = intake.set_section_state(state, S1, "추가자료요청", note, owner=owner)
                for language in ("ko", "en"):
                    rows = list(csv.reader(io.StringIO(intake.request_csv(state, lang=language).decode("utf-8-sig"))))
                    cells = [cell for row in rows[1:] for cell in row]
                    self.assertTrue(any(name in cell for cell in cells), "Filename missing from request CSV")
                    self.assertTrue(any(note in cell for cell in cells), "Request text missing from CSV")
                    self.assertTrue(any(owner in cell for cell in cells), "Owner missing from CSV")
                    for cell in cells:
                        self.assertFalse(cell.lstrip(" \t\r\n").startswith(("=", "+", "-", "@")),
                                         f"Executable spreadsheet cell: {cell!r}")

    def test_csv_neutralizes_formulas_hidden_by_bom_zero_width_and_whitespace(self):
        for prefix in ("\ufeff", "\u200b", "\ufeff\u200b \t", " \t\ufeff\u200b "):
            with self.subTest(prefix=repr(prefix)):
                note = prefix + '=HYPERLINK("https://example.invalid","open")'
                state = intake.set_section_state(intake.new_intake(), S1, "추가자료요청", note)
                stored_note = self.row(state, S1)["request"]
                for language in ("ko", "en"):
                    rows = list(csv.reader(io.StringIO(intake.request_csv(state, lang=language).decode("utf-8-sig"))))
                    cells = [cell for row in rows[1:] for cell in row]
                    self.assertIn("'" + stored_note, cells)
                    self.assertNotIn(stored_note, cells)

    def test_manifest_contains_metadata_and_explicitly_excludes_original_content(self):
        content = b"Synthetic confidential marker 938573275"
        state = self.upload(name="received.txt", content=content, sections=(S1, S2))
        before = copy.deepcopy(state)
        raw = intake.manifest_json(state)
        self.assertIsInstance(raw, bytes)
        manifest = json.loads(raw)
        self.assertEqual(manifest["schema_version"], 1)
        self.assertNotIn("content", set(all_keys(manifest)))
        self.assertNotIn(content, raw)
        self.assertIn(b"received.txt", raw)
        self.assertIn(hashlib.sha256(content).hexdigest().encode("ascii"), raw)
        text = raw.decode("utf-8").lower()
        self.assertTrue("metadata" in text or "메타" in text,
                        "Manifest must explain that it only exports metadata")
        self.assertEqual(state, before)

    def test_file_metadata_excludes_content_without_mutating_or_sharing_state(self):
        state = self.upload(sections=(S1, S2))
        before = copy.deepcopy(state)
        rows = intake.file_metadata(state)
        self.assertIsInstance(rows, list)
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertNotIn("content", row)
        for key in ("id", "sha256", "name", "size", "type", "extension", "sections"):
            self.assertIn(key, row)
        self.assertEqual(set(row["sections"]), {S1, S2})
        self.assertEqual(row["section_ids"], row["sections"])
        self.assertEqual(row["content_type"], row["type"])
        self.assertEqual(state, before)
        row["name"] = "must-not-change-source.pdf"
        if isinstance(row["sections"], list):
            row["sections"].append("test-section")
        self.assertEqual(state, before)


if __name__ == "__main__":
    unittest.main(verbosity=2)

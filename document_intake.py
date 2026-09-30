"""Session-only document receipt registry, independent of the review workbench.

This module never writes files, parses document text, or changes reviewed
evidence. A file's presence means only that it awaits review. Functions return
new registry dictionaries so a UI can commit several uploads atomically.
"""
from __future__ import annotations

import copy
import csv
from datetime import date
import hashlib
import io
import json
from pathlib import PurePosixPath
import unicodedata
import zipfile


MAX_FILE_BYTES = 20 * 1024 * 1024
MAX_TOTAL_BYTES = 100 * 1024 * 1024
MAX_FILES = 50
ALLOWED_EXTENSIONS = ("pdf", "docx", "xlsx", "txt", "doc", "xls")
STATUSES = ("정보없음", "검토대기", "추가자료요청", "해당없음")
PRIORITIES = ("높음", "보통", "낮음")
_MIME_TYPES = {
    "pdf": {"application/pdf"},
    "docx": {"application/vnd.openxmlformats-officedocument.wordprocessingml.document"},
    "xlsx": {"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"},
    "txt": {"text/plain"},
    "doc": {"application/msword"},
    "xls": {"application/vnd.ms-excel"},
}
_GENERIC_MIME_TYPES = {"", "application/octet-stream", "binary/octet-stream"}

_S_SECTIONS = (
    ("일반정보", "General information"),
    ("제조", "Manufacture"),
    ("특성규명", "Characterisation"),
    ("원료의약품 관리", "Control of drug substance"),
    ("표준품·표준물질", "Reference standards or materials"),
    ("용기·포장", "Container closure system"),
    ("안정성", "Stability"),
)
_P_SECTIONS = (
    ("제품 개요·조성", "Description and composition"),
    ("개발 경위", "Pharmaceutical development"),
    ("제조", "Manufacture"),
    ("첨가제 관리", "Control of excipients"),
    ("완제의약품 관리", "Control of drug product"),
    ("표준품·표준물질", "Reference standards or materials"),
    ("용기·포장", "Container closure system"),
    ("안정성", "Stability"),
)


def _section(section_id, group, code, ko, en):
    return {"id": section_id, "group": group, "code": code,
            "label_ko": ko, "label_en": en}


# 3.2.S and 3.2.P are groups, not extra missing-document rows. DMF and CTD
# sections stay distinct: users must explicitly map a shared file to both.
SECTION_CATALOG = tuple(
    [_section("DMF.ADMIN", "DMF", "ADMIN", "행정자료·참조권한(LoA)",
              "Administrative access / LoA")]
    + [_section(f"DMF.S.{i}", "DMF", f"S.{i}", ko, en)
       for i, (ko, en) in enumerate(_S_SECTIONS, 1)]
    + [_section("CTD.1", "CTD 1", "1", "행정·지역별 자료", "Regional administrative information"),
       _section("CTD.2", "CTD 2", "2", "CTD 요약", "CTD summaries")]
    + [_section(f"CTD.3.2.S.{i}", "CTD 3.2.S", f"3.2.S.{i}", ko, en)
       for i, (ko, en) in enumerate(_S_SECTIONS, 1)]
    + [_section(f"CTD.3.2.P.{i}", "CTD 3.2.P", f"3.2.P.{i}", ko, en)
       for i, (ko, en) in enumerate(_P_SECTIONS, 1)]
    + [_section("CTD.4", "CTD 4", "4", "비임상시험 보고서", "Nonclinical study reports"),
       _section("CTD.5", "CTD 5", "5", "임상시험 보고서", "Clinical study reports")]
)
_SECTIONS = {section["id"]: section for section in SECTION_CATALOG}


def new_intake() -> dict:
    """Create an empty registry. Legacy sample evidence is never imported."""
    return {
        "schema_version": 1,
        "files": {},
        "section_states": {
            key: {"status": "정보없음", "note": "", "owner": "",
                  "due_date": "", "priority": "보통"}
            for key in _SECTIONS
        },
    }


def _check_state(state):
    if (not isinstance(state, dict) or state.get("schema_version") != 1
            or not isinstance(state.get("files"), dict)
            or not isinstance(state.get("section_states"), dict)):
        raise ValueError("Invalid document intake registry.")


def _check_section(section_id):
    if not isinstance(section_id, str) or section_id not in _SECTIONS:
        raise ValueError("Unknown document section.")


def _section_ids(section_ids):
    if isinstance(section_ids, (str, bytes)) or not isinstance(section_ids, (list, tuple, set)):
        raise ValueError("Select one or more document sections.")
    if not section_ids:
        raise ValueError("Select one or more document sections.")
    for section_id in section_ids:
        _check_section(section_id)
    # Catalog order makes manifests reproducible, including set inputs.
    return [key for key in _SECTIONS if key in section_ids]


def safe_filename(name: str) -> str:
    """Drop path components and control characters; retain a readable name."""
    if not isinstance(name, str):
        raise ValueError("A filename is required.")
    name = unicodedata.normalize("NFC", name).replace("\\", "/").split("/")[-1]
    name = "".join(char for char in name if not unicodedata.category(char).startswith("C"))
    name = "".join("_" if char in '<>:"|?*' else char for char in name)
    name = name.strip().rstrip(". ")
    if name in {"", ".", ".."}:
        raise ValueError("A valid filename is required.")
    suffix = PurePosixPath(name).suffix
    if name.split(".", 1)[0].upper() in {"CON", "PRN", "AUX", "NUL"} | {
            f"{prefix}{number}" for prefix in ("COM", "LPT") for number in range(1, 10)}:
        name = "_" + name
    if len(name) > 180:
        name = name[:180 - len(suffix)] + suffix
    return name


def _validate_content(extension: str, content: bytes) -> None:
    if extension == "pdf":
        if not content.startswith(b"%PDF-"):
            raise ValueError("PDF content does not match the filename.")
    elif extension in {"doc", "xls"}:
        if not content.startswith(bytes.fromhex("D0CF11E0A1B11AE1")) or len(content) < 512:
            raise ValueError("Legacy DOC/XLS content must be an OLE document.")
    elif extension in {"docx", "xlsx"}:
        expected = "word/document.xml" if extension == "docx" else "xl/workbook.xml"
        try:
            with zipfile.ZipFile(io.BytesIO(content)) as archive:
                entries = archive.infolist()
                names = {entry.filename for entry in entries}
                if len(entries) > 10000 or sum(entry.file_size for entry in entries) > 200 * 1024 * 1024:
                    raise ValueError("Office document archive is too large.")
                if "[Content_Types].xml" not in names or expected not in names:
                    raise ValueError("Office document content does not match the filename.")
        except (zipfile.BadZipFile, OSError, RuntimeError) as exc:
            raise ValueError("Invalid Office document archive.") from exc
    else:
        try:
            encoding = "utf-16" if content.startswith((b"\xff\xfe", b"\xfe\xff")) else "utf-8-sig"
            decoded = content.decode(encoding)
        except UnicodeDecodeError as exc:
            raise ValueError("TXT files must use UTF-8 or UTF-16 with a byte-order mark.") from exc
        if not decoded.strip() or any(unicodedata.category(c) == "Cc" and c not in "\t\n\r\f" for c in decoded):
            raise ValueError("TXT content is empty or contains binary control characters.")


def validate_file(name: str, content: bytes, content_type: str = "") -> dict:
    """Validate bounded bytes and return metadata, without retaining or writing them.

    Signature/container checks detect common wrong-format uploads. They are not
    malware scanning, full document validation, or document text extraction.
    """
    name = safe_filename(name)
    extension = PurePosixPath(name).suffix.lower().lstrip(".")
    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError("Allowed file types: PDF, DOCX, XLSX, TXT, DOC, XLS.")
    if not isinstance(content, bytes) or not content:
        raise ValueError("A nonempty byte payload is required.")
    if len(content) > MAX_FILE_BYTES:
        raise ValueError("Each file must be 20 MiB or smaller.")
    if not isinstance(content_type, str):
        raise ValueError("Invalid file content type.")
    mime_type = content_type.split(";", 1)[0].strip().lower()
    if mime_type not in _MIME_TYPES[extension] | _GENERIC_MIME_TYPES:
        raise ValueError("The supplied content type does not match the filename.")
    _validate_content(extension, content)
    digest = hashlib.sha256(content).hexdigest()
    canonical_type = next(iter(_MIME_TYPES[extension]))
    return {"id": digest, "sha256": digest, "name": name, "size": len(content),
            "type": canonical_type, "content_type": canonical_type, "extension": extension}


def _files_for_section(state, section_id):
    return [record for record in state["files"].values() if section_id in record["sections"]]


def section_status(state: dict, section_id: str) -> str:
    _check_state(state)
    _check_section(section_id)
    decision = state["section_states"].get(section_id, {}).get("status", "정보없음")
    if decision in {"추가자료요청", "해당없음"}:
        return decision
    return "검토대기" if _files_for_section(state, section_id) else "정보없음"


def _refresh_statuses(state):
    for section_id in _SECTIONS:
        state["section_states"][section_id]["status"] = section_status(state, section_id)


def add_file(state: dict, name: str, content: bytes, section_ids, content_type: str = "") -> dict:
    """Register RAM bytes; identical content is deduplicated and mappings unioned."""
    _check_state(state)
    sections = _section_ids(section_ids)
    metadata = validate_file(name, content, content_type)
    file_id = metadata["id"]
    if file_id not in state["files"]:
        if len(state["files"]) >= MAX_FILES:
            raise ValueError("A session may contain at most 50 files.")
        if sum(record["size"] for record in state["files"].values()) + len(content) > MAX_TOTAL_BYTES:
            raise ValueError("Session files must total 100 MiB or less.")
    result = copy.deepcopy(state)
    if file_id in result["files"]:
        record = result["files"][file_id]
        if record["extension"] != metadata["extension"]:
            raise ValueError("Identical content is already registered with a different file type.")
        record["sections"] = _section_ids(record["sections"] + sections)
        record["section_ids"] = list(record["sections"])
    else:
        result["files"][file_id] = {**metadata, "sections": sections,
                                    "section_ids": list(sections), "content": content}
    _refresh_statuses(result)
    return result


def reassign_file(state: dict, file_id: str, section_ids) -> dict:
    """Replace a file's section mappings without copying into reviewed evidence."""
    _check_state(state)
    sections = _section_ids(section_ids)
    if file_id not in state["files"]:
        raise ValueError("File is not in this session.")
    result = copy.deepcopy(state)
    result["files"][file_id]["sections"] = sections
    result["files"][file_id]["section_ids"] = list(sections)
    _refresh_statuses(result)
    return result


def delete_file(state: dict, file_id: str) -> dict:
    _check_state(state)
    if file_id not in state["files"]:
        raise ValueError("File is not in this session.")
    result = copy.deepcopy(state)
    del result["files"][file_id]
    _refresh_statuses(result)
    return result


def _text(value, field, limit):
    if not isinstance(value, str) or len(value) > limit or "\x00" in value:
        raise ValueError(f"Invalid {field} (maximum {limit} characters).")
    return value.strip()


def set_section_state(state: dict, section_id: str, status: str, note: str = "", *,
                      owner: str = "", due_date: str = "", priority: str = "보통") -> dict:
    """Save an explicit receipt decision; no approved/ready status exists here."""
    _check_state(state)
    _check_section(section_id)
    if status not in STATUSES:
        raise ValueError("Unsupported document receipt status.")
    has_files = bool(_files_for_section(state, section_id))
    if status == "검토대기" and not has_files:
        raise ValueError("No file is available for review in this section.")
    if status == "정보없음" and has_files:
        raise ValueError("Remove or reassign attached files before marking this section as missing.")
    if priority not in PRIORITIES:
        raise ValueError("Invalid request priority.")
    note = _text(note, "request", 4000)
    owner = _text(owner, "owner", 200)
    due_date = _text(due_date, "due date", 10)
    if due_date:
        try:
            if date.fromisoformat(due_date).isoformat() != due_date:
                raise ValueError
        except ValueError as exc:
            raise ValueError("Due date must use YYYY-MM-DD.") from exc
    result = copy.deepcopy(state)
    result["section_states"][section_id] = {
        "status": status, "note": note, "owner": owner,
        "due_date": due_date, "priority": priority,
    }
    return result


def file_metadata(state: dict) -> list[dict]:
    _check_state(state)
    return [copy.deepcopy({key: value for key, value in record.items() if key != "content"})
            for record in state["files"].values()]


def summary_rows(state: dict) -> list[dict]:
    _check_state(state)
    rows = []
    for section in SECTION_CATALOG:
        section_id = section["id"]
        files = _files_for_section(state, section_id)
        decision = state["section_states"].get(section_id, {})
        rows.append({
            "section_id": section_id,
            **{key: section[key] for key in ("group", "code", "label_ko", "label_en")},
            "status": section_status(state, section_id),
            "file_count": len(files), "file_names": "; ".join(record["name"] for record in files),
            "request": decision.get("note", ""), "owner": decision.get("owner", ""),
            "due_date": decision.get("due_date", ""), "priority": decision.get("priority", "보통"),
        })
    return rows


def request_rows(state: dict, lang: str = "ko") -> list[dict]:
    if lang not in {"ko", "en"}:
        raise ValueError("Unsupported request language.")
    rows = []
    for row in summary_rows(state):
        if row["status"] not in {"정보없음", "추가자료요청"}:
            continue
        if not row["request"]:
            if row["status"] == "추가자료요청":
                row["request"] = ("추가로 필요한 자료와 확인사항을 구체적으로 기재해 주세요."
                                  if lang == "ko" else "Specify the additional documents and clarification needed.")
            else:
                row["request"] = (f"{row['code']} {row['label_ko']} 자료를 제공하거나 해당없음 여부를 확인해 주세요."
                                  if lang == "ko" else
                                  f"Provide documents for {row['code']} {row['label_en']}, or confirm that it is not applicable.")
        rows.append(row)
    return rows


def _csv_safe(value) -> str:
    text = str(value)
    candidate = text
    while candidate and (candidate[0].isspace() or unicodedata.category(candidate[0]).startswith("C")):
        candidate = candidate[1:]
    if candidate.startswith(("=", "+", "-", "@")) or text.startswith(("\t", "\r", "\n")):
        return "'" + text
    return text


def request_csv(state: dict, lang: str = "ko") -> bytes:
    """Export requests only; escape spreadsheet formulas and include a UTF-8 BOM."""
    rows = request_rows(state, lang)
    fields = ["section_id", "group", "code", f"label_{lang}", "receipt", "status", "file_count",
              "file_names", "request", "owner", "due_date", "priority"]
    headers = (["섹션 ID", "자료 구분", "섹션", "제목", "접수 상태", "검토 상태", "파일 수", "첨부파일",
                "추가정보 요청", "담당자", "요청기한", "우선순위"] if lang == "ko" else
               ["Section ID", "Group", "Section", "Title", "Receipt status", "Review state", "File count", "Files",
                "Information request", "Owner", "Due date", "Priority"])
    out = io.StringIO(newline="")
    writer = csv.writer(out)
    writer.writerow(headers)
    status_en = dict(zip(STATUSES, ("No information", "Pending review", "Additional information requested", "Not applicable")))
    priority_en = dict(zip(PRIORITIES, ("High", "Normal", "Low")))
    for row in rows:
        receipt = ("해당없음" if row["status"] == "해당없음" else
                   "파일 접수" if row["file_count"] else "정보없음")
        row = {**row, "receipt": receipt}
        if lang == "en":
            row = {**row, "status": status_en[row["status"]], "priority": priority_en[row["priority"]],
                   "receipt": {"해당없음": "Not applicable", "파일 접수": "Files received",
                               "정보없음": "No information"}[receipt]}
        writer.writerow([_csv_safe(row[field]) for field in fields])
    return out.getvalue().encode("utf-8-sig")


def manifest_json(state: dict) -> bytes:
    """Download metadata, not the uploaded files or a restorable evidence package."""
    _check_state(state)
    payload = {"schema_version": 1, "kind": "document_intake_metadata",
               "contains_file_contents": False, "files": file_metadata(state),
               "sections": summary_rows(state),
               "note": "Metadata only; attachment presence is not evidence review or approval."}
    return json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")

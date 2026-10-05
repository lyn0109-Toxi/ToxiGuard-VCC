"""Explicit, session-scoped provenance and version comparison for uploaded files."""
from __future__ import annotations

import copy
from datetime import date
import difflib
from html import escape
import uuid

DOCUMENT_FIELDS = ("version", "system", "source", "product", "batch", "stage", "effective_date", "reviewer")
STATUSES = ("unconfirmed", "confirmed", "conflicting")


def source_label(ref):
    if not ref:
        return ""
    if ref.get("format") == "pdf":
        return f"Page {ref.get('page', '')}"
    if ref.get("format") == "txt":
        return f"Line {ref.get('line', '')}"
    if ref.get("format") == "xlsx":
        return str(ref.get("sheet", "")) + "!" + ", ".join(map(str, ref.get("cells", [])))
    if ref.get("table") is not None:
        return f"Table {ref['table']} / row {ref.get('row', '')} / cells " + ", ".join(map(str, ref.get("cells", [])))
    return f"Paragraph {ref.get('paragraph', '')}"


def new_trace():
    return {"documents": {}, "evidence": []}


def prune_trace(trace, files):
    result = copy.deepcopy(trace)
    result["documents"] = {key: value for key, value in result["documents"].items() if key in files}
    result["evidence"] = [item for item in result["evidence"] if item["file_id"] in files]
    return result


def save_document(trace, file_id, metadata):
    result = copy.deepcopy(trace)
    document = {field: str(metadata.get(field, "")).strip()[:2000] for field in DOCUMENT_FIELDS}
    status = metadata.get("status", "unconfirmed")
    if status not in STATUSES:
        raise ValueError("Unknown confirmation status.")
    if document["effective_date"]:
        date.fromisoformat(document["effective_date"])
    if status == "confirmed" and any(not document[field] for field in ("version", "source", "product", "batch", "stage", "reviewer")):
        raise ValueError("Confirmation needs version, source, product, batch scope, stage and reviewer.")
    previous = result["documents"].get(file_id, {})
    if previous and (any(previous.get(field, "") != document[field] for field in DOCUMENT_FIELDS)
                     or (previous.get("status") == "confirmed" and status != "confirmed")):
        for evidence in result["evidence"]:
            if evidence["file_id"] == file_id:
                evidence["status"] = "unconfirmed"
                evidence["invalidation"] = "Document version, applicability metadata or confirmation changed; recheck the source."
    document["status"] = status
    result["documents"][file_id] = document
    return result


def save_evidence(trace, file_id, candidate, review):
    result = copy.deepcopy(trace)
    status = review.get("status", "unconfirmed")
    if status not in STATUSES:
        raise ValueError("Unknown confirmation status.")
    if not candidate.get("excerpt") or not candidate.get("location"):
        raise ValueError("A source excerpt and location are required.")
    document = result["documents"].get(file_id, {})
    if status == "confirmed" and (document.get("status") != "confirmed" or not review.get("reviewer", "").strip() or not review.get("confirmed_value", "").strip()):
        raise ValueError("Confirm document applicability, enter the checked value and name the reviewer first.")
    due = str(review.get("due_date", ""))
    if due:
        date.fromisoformat(due)
    evidence = {"id": str(uuid.uuid4()), "file_id": file_id,
                "topic": candidate.get("topic", ""), "location": candidate["location"],
                "source_ref": copy.deepcopy(candidate.get("source_ref", {})), "excerpt": candidate["excerpt"],
                "document_snapshot": copy.deepcopy(document), "status": status}
    for field in ("confirmed_value", "reviewer", "ctd_target", "request", "owner", "due_date", "impact"):
        evidence[field] = str(review.get(field, "")).strip()[:4000]
    # The same topic/location is an editable review record, not duplicate requests.
    result["evidence"] = [old for old in result["evidence"] if (old["file_id"], old["topic"], old["location"]) != (file_id, evidence["topic"], evidence["location"])]
    result["evidence"].append(evidence)
    return result


def applicability(document, product, batch="", stage=""):
    if document and document.get("status") == "conflicting":
        return "conflicting"
    if not document or document.get("status") != "confirmed":
        return "unconfirmed"
    expected = {"product": product, "batch": batch, "stage": stage}
    if any(value and document.get(field, "").casefold() != str(value).strip().casefold() for field, value in expected.items()):
        return "scope_mismatch"
    return "confirmed" if product and batch and stage else "unconfirmed"


def compare_documents(old_result, new_result):
    if old_result.get("status") != "ok" or new_result.get("status") != "ok":
        raise ValueError("Both documents need readable extracted text.")
    def lines(result):
        found = []
        for unit in result["units"]:
            for text in unit["text"].splitlines():
                if text.strip():
                    found.append({"text": text.strip(), "location": unit["location"], "source_ref": unit.get("source_ref", {})})
                    if len(found) > 2000:
                        return found[:2000], True
        return found, False
    old, old_cut = lines(old_result)
    new, new_cut = lines(new_result)
    changes = []
    for action, a, b, c, d in difflib.SequenceMatcher(None, [line["text"] for line in old], [line["text"] for line in new], autojunk=True).get_opcodes():
        if action != "equal":
            changes.append({"change": action, "old": old[a:b][:20], "new": new[c:d][:20],
                            "truncated": b - a > 20 or d - c > 20})
    return {"changes": changes, "partial": bool(old_cut or new_cut or old_result.get("truncated") or new_result.get("truncated"))}


def trace_report(trace, files, lang="en", profile=None):
    trace = prune_trace(trace, files)
    if not trace["documents"] and not trace["evidence"]:
        return ""
    title = "문서 버전·적용 범위와 출처 검토" if lang == "ko" else "Document versions, applicability and source review"
    note = "추출·변경 탐지는 확인된 적용 근거가 아닙니다. 미확인·범위 불일치는 별도 확인하세요." if lang == "ko" else "Extraction and detected text changes are not confirmed applicability evidence. Check unconfirmed records and scope mismatches."
    documents = [{"file_name": files[key]["name"], "sha256": key, **value,
                  "current_scope": applicability(value, (profile or {}).get("product", ""), (profile or {}).get("batch", ""), (profile or {}).get("stage", ""))}
                 for key, value in trace["documents"].items()]
    evidence = [{"file_name": files[item["file_id"]]["name"], **item} for item in trace["evidence"]]
    def table(headers, rows):
        def clean(value):
            return escape(str(value), quote=False).replace("|", "\\|").replace("\r", " ").replace("\n", "<br>")
        return "\n".join(["| " + " | ".join(map(clean, headers)) + " |",
                          "| " + " | ".join("---" for _ in headers) + " |",
                          *["| " + " | ".join(map(clean, row)) + " |" for row in rows]])
    ko = lang == "ko"
    document_headers = (["문서", "버전 / 시스템", "출처", "제품", "배치", "단계", "확인 상태", "현재 범위"] if ko else
                        ["Document", "Version / system", "Source", "Product", "Batch", "Stage", "Confirmation", "Current scope"])
    document_rows = [[item["file_name"], f"{item['version']} / {item['system']}", item["source"], item["product"], item["batch"], item["stage"], item["status"], item["current_scope"]] for item in documents]
    evidence_headers = (["문서 · 버전 · 위치", "확인값 / 해석", "상태", "변경 영향 / 원문", "CTD 위치", "추가자료", "담당자", "기한"] if ko else
                        ["Document · version · location", "Checked value / interpretation", "Status", "Impact / source", "CTD location", "Information needed", "Owner", "Due date"])
    evidence_rows = [[f"{item['file_name']} · {item['document_snapshot'].get('version', '')} · {item['location']} · {source_label(item['source_ref'])}", item["confirmed_value"], item["status"],
                      f"{item['impact']} / {item['excerpt']} / {item.get('invalidation', '')}", item["ctd_target"], item["request"], item["owner"], item["due_date"]] for item in evidence]
    return f"\n## {title}\n\n{note}\n\n" + table(document_headers, document_rows) + "\n\n" + table(evidence_headers, evidence_rows) + "\n"

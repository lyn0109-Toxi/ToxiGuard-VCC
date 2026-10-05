"""Bounded, local extraction of document evidence; no review-state mutation."""
from __future__ import annotations

import base64
import io
import json
from pathlib import Path
import posixpath
import re
import subprocess
import sys
import zipfile

MAX_CHARS = 300_000
MAX_UNITS = 2_000
MAX_PAGES = 120
MAX_FILE_BYTES = 20 * 1024 * 1024
MAX_ARCHIVE_MEMBERS = 2_000
MAX_ARCHIVE_BYTES = 64 * 1024 * 1024
MAX_XML_BYTES = 20 * 1024 * 1024
MAX_XLSX_SHEETS = 32
MAX_XLSX_CELLS = 20_000
MAX_SHARED_STRINGS = 30_000


class _ExtractionLimit(Exception):
    """An archive or its extracted content exceeds an explicit bound."""


class _EncryptedArchive(Exception):
    """Encrypted ZIP members are not read by the extraction worker."""

# Keyword matches are navigation aids, never findings of compliance.
TOPICS = (
    ("identity", "약물명·제품 조성", "Identity / composition", r"drug substance|drug product|active ingredient|composition|약물명|제품명|성분명|주성분|조성", "명칭·함량·제형이 일치하는지 확인", "Check identity, strength and dosage form consistency"),
    ("manufacture", "제조·공정", "Manufacture / process", r"manufactur(?:e|ing|er)|process control|batch formula|제조|공정", "제조소·공정·관리항목 확인", "Check sites, process steps and controls"),
    ("specification", "규격·허용기준", "Specifications / limits", r"specification|acceptance criteri|assay|규격|허용기준|함량시험", "규격 수치·단위·설정 근거 확인", "Check specification values, units and rationale"),
    ("methods", "시험법·밸리데이션", "Methods / validation", r"analytical procedure|analytical method|validation|accuracy|precision|LOD|LOQ|시험법|밸리데이션|정확성|정밀성", "시험법과 밸리데이션 결과·기준 대조", "Compare methods, validation results and criteria"),
    ("impurities", "불순물·잔류물", "Impurities / residues", r"impurit|related substances|residual solvent|elemental|PDE|TDI|불순물|유연물질|잔류용매", "불순물별 기준·노출량·분석 근거 확인", "Check impurity limits, exposure and analytical evidence"),
    ("stability", "안정성·사용기간", "Stability / shelf life", r"stability|shelf.life|retest|storage|안정성|사용기간|재시험|보관조건", "보관조건·시점별 결과·사용기간 근거 확인", "Check storage conditions, time-point results and shelf-life rationale"),
    ("packaging", "용기·포장", "Container / closure", r"container|closure|packaging|용기|포장", "재질·적합성·제품 보호 근거 확인", "Check materials, suitability and product protection"),
    ("nonclinical", "비임상·독성", "Nonclinical / toxicology", r"nonclinical|toxicology|toxicity|비임상|독성", "시험 설계·노출량·독성 결과 확인", "Check study design, exposure and toxicity results"),
    ("clinical", "임상·안전성", "Clinical / safety", r"(?<!non)\bclinical|efficacy|adverse event|임상시험|유효성|이상반응", "임상 설계·유효성·안전성 근거 확인", "Check clinical design, efficacy and safety evidence"),
)
DRUG_PATTERN = re.compile(
    r"(?:drug substance(?: name)?|drug product(?: name)?|product name|active ingredient|INN|약물명|제품명|성분명|주성분|유효성분)"
    r"\s*[:：=\t]\s*([^\n\r;\t|]{2,100})", re.I)
SECTION_PATTERN = re.compile(r"(?<![\w.])(?:3\s*\.\s*2\s*\.\s*[SP](?:\s*\.\s*[1-8]){0,2}|(?:Module|모듈)\s*[1-5])(?![\w.])", re.I)


def analyse_units(units: list[dict], truncated: bool = False) -> dict:
    drugs, sections, topics = [], [], []
    drug_seen, section_seen = set(), set()
    chars = 0
    kept = []
    for unit in units[:MAX_UNITS]:
        text = unit["text"][:max(0, MAX_CHARS - chars)]
        if not text:
            continue
        chars += len(text)
        kept.append({"location": unit["location"], "text": text,
                     "source_ref": dict(unit.get("source_ref", {})),
                     "review_status": "unconfirmed",
                     "_source_spans": unit.get("_source_spans", [])})
        if chars >= MAX_CHARS:
            truncated = True
            break
    truncated |= len(units) > MAX_UNITS
    for unit in kept:
        for match in DRUG_PATTERN.finditer(unit["text"]):
            name = match.group(1).strip()
            if name.casefold() not in drug_seen and len(drugs) < 20:
                drug_seen.add(name.casefold())
                drugs.append({"name": name, "location": unit["location"], "excerpt": match.group(0),
                              "source_ref": _reference(unit, match.start(), match.end()),
                              "review_status": "unconfirmed"})
        for match in SECTION_PATTERN.finditer(unit["text"]):
            code = re.sub(r"\s+", "", match.group(0)).upper()
            if code not in section_seen and len(sections) < 80:
                section_seen.add(code)
                sections.append({"section": code, "location": unit["location"], "excerpt": _excerpt(unit["text"], match.start()),
                                 "source_ref": _reference(unit, match.start(), match.end()),
                                 "review_status": "unconfirmed"})
    for key, ko, en, pattern, review_ko, review_en in TOPICS:
        regex = re.compile(pattern, re.I)
        evidence, matches = [], 0
        for unit in kept:
            match = regex.search(unit["text"])
            if match:
                matches += 1
                if len(evidence) < 5:
                    evidence.append({"location": unit["location"], "excerpt": _excerpt(unit["text"], match.start()),
                                     "source_ref": _reference(unit, match.start(), match.end()),
                                     "review_status": "unconfirmed"})
        topics.append({"key": key, "ko": ko, "en": en, "review_ko": review_ko,
                       "review_en": review_en, "matches": matches, "evidence": evidence})
    for unit in kept:
        unit.pop("_source_spans", None)
    return {"status": "ok" if chars else "empty", "characters": chars,
            "review_status": "unconfirmed",
            "truncated": bool(truncated), "drugs": drugs, "sections": sections,
            "topics": topics, "units": kept}


def _excerpt(text: str, start: int) -> str:
    return text[max(0, start - 90):start + 260].strip()


def _reference(unit: dict, start: int, end: int) -> dict:
    """Identify cells containing the matched candidate without judging evidence."""
    reference = dict(unit.get("source_ref", {}))
    spans = unit.get("_source_spans", [])
    if spans:
        reference["cells"] = [span["cell"] for span in spans
                              if span["start"] < end and span["end"] > start]
        if "formula_cells" in reference:
            reference["formula_cells"] = [cell for cell in reference["formula_cells"]
                                          if cell in reference["cells"]]
    return reference


def _row_unit(location: str, reference: dict, cells: list[tuple]) -> dict:
    parts, spans, offset = [], [], 0
    for cell, value in cells:
        parts.append(value)
        spans.append({"cell": cell, "start": offset, "end": offset + len(value)})
        offset += len(value) + 1
    raw = "\t".join(parts)
    trim = len(raw) - len(raw.lstrip())
    for span in spans:
        span["start"] -= trim
        span["end"] -= trim
    return {"location": location, "text": raw.strip(), "source_ref": reference,
            "_source_spans": spans}


def _check_archive(archive: zipfile.ZipFile) -> None:
    members = archive.infolist()
    if (len(members) > MAX_ARCHIVE_MEMBERS
            or sum(member.file_size for member in members) > MAX_ARCHIVE_BYTES
            or any(member.file_size > MAX_XML_BYTES for member in members)):
        raise _ExtractionLimit
    if len({member.filename for member in members}) != len(members):
        raise ValueError("Duplicate archive member")
    if any(member.flag_bits & 1 for member in members):
        raise _EncryptedArchive


def _xml(archive: zipfile.ZipFile, name: str):
    from defusedxml.ElementTree import fromstring
    if archive.getinfo(name).file_size > MAX_XML_BYTES:
        raise _ExtractionLimit
    return fromstring(archive.read(name))


def _xlsx_units(content: bytes) -> tuple[list[dict], bool]:
    """Read cached XLSX values locally; never evaluate formulas or external links."""
    ns = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
    rel_ns = "{http://schemas.openxmlformats.org/package/2006/relationships}"
    office_rel = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
    units, chars, cell_count, truncated = [], 0, 0, False
    with zipfile.ZipFile(io.BytesIO(content)) as archive:
        _check_archive(archive)
        workbook = _xml(archive, "xl/workbook.xml")
        if workbook.tag != ns + "workbook":
            raise ValueError("Invalid workbook")
        relationships = _xml(archive, "xl/_rels/workbook.xml.rels")
        relations = {node.get("Id"): node for node in relationships.findall(rel_ns + "Relationship")}
        shared = []
        if "xl/sharedStrings.xml" in archive.namelist():
            strings = _xml(archive, "xl/sharedStrings.xml")
            for index, item in enumerate(strings.findall(ns + "si")):
                if index >= MAX_SHARED_STRINGS:
                    raise _ExtractionLimit
                shared.append("".join(node.text or "" for node in item.iter(ns + "t")))
        sheets = workbook.find(ns + "sheets")
        if sheets is None:
            raise ValueError("Missing worksheet list")
        sheet_nodes = sheets.findall(ns + "sheet")
        truncated = len(sheet_nodes) > MAX_XLSX_SHEETS
        for sheet in sheet_nodes[:MAX_XLSX_SHEETS]:
            name = sheet.get("name")
            relation = relations.get(sheet.get(office_rel + "id"))
            if not name or relation is None or relation.get("TargetMode") == "External":
                raise ValueError("Invalid worksheet relationship")
            if not relation.get("Type", "").endswith("/worksheet"):
                raise ValueError("Invalid worksheet type")
            target = relation.get("Target", "")
            path = posixpath.normpath(target.lstrip("/") if target.startswith("/")
                                     else posixpath.join("xl", target))
            if not path.startswith("xl/") or "\\" in path:
                raise ValueError("Invalid worksheet path")
            root = _xml(archive, path)
            if root.tag != ns + "worksheet":
                raise ValueError("Invalid worksheet")
            data = root.find(ns + "sheetData")
            if data is None:
                continue
            for ordinal, row in enumerate(data.findall(ns + "row"), 1):
                row_number = int(row.get("r", str(ordinal)))
                if not 1 <= row_number <= 1_048_576:
                    raise ValueError("Invalid worksheet row")
                cells, seen_cells, formula_cells, row_chars, row_truncated = [], set(), [], 0, False
                for cell in row.findall(ns + "c"):
                    cell_count += 1
                    if cell_count > MAX_XLSX_CELLS:
                        truncated = True
                        break
                    address = cell.get("r", "").upper()
                    match = re.fullmatch(r"([A-Z]{1,3})([1-9][0-9]{0,6})", address)
                    if not match or int(match.group(2)) != row_number or address in seen_cells:
                        raise ValueError("Invalid worksheet cell")
                    column = 0
                    for char in match.group(1):
                        column = column * 26 + ord(char) - ord("A") + 1
                    if column > 16_384:
                        raise ValueError("Invalid worksheet column")
                    seen_cells.add(address)
                    if cell.find(ns + "f") is not None:
                        formula_cells.append(address)
                    kind = cell.get("t", "n")
                    value = cell.find(ns + "v")
                    if kind == "inlineStr":
                        inline = cell.find(ns + "is")
                        text = "".join(node.text or "" for node in inline.iter(ns + "t")) if inline is not None else ""
                    elif kind == "s":
                        index = int(value.text) if value is not None and value.text is not None else -1
                        if not 0 <= index < len(shared):
                            raise ValueError("Invalid shared string reference")
                        text = shared[index]
                    else:
                        # Formula cells are represented only by their stored result.
                        text = value.text or "" if value is not None else ""
                    if text.strip():
                        remaining = max(0, MAX_CHARS - chars - row_chars)
                        if len(text) > remaining:
                            text = text[:remaining]
                            row_truncated = True
                        cells.append((address, text))
                        row_chars += len(text) + 1
                        if row_truncated or row_chars >= MAX_CHARS - chars:
                            row_truncated = True
                            break
                if cells:
                    reference = {"format": "xlsx", "sheet": name, "row": row_number,
                                 "cells": [address for address, _ in cells],
                                 "value_mode": "stored_values"}
                    if formula_cells:
                        reference["formula_cells"] = formula_cells
                    unit = _row_unit(f"Sheet {name}, row {row_number}", reference, cells)
                    units.append(unit)
                    chars += len(unit["text"])
                if row_truncated or cell_count > MAX_XLSX_CELLS or chars >= MAX_CHARS or len(units) >= MAX_UNITS:
                    return units, True
    return units, truncated


def _extract(name: str, content: bytes) -> dict:
    extension = Path(name).suffix.lower()
    units, truncated = [], False
    if extension == ".txt":
        encoding = "utf-16" if content.startswith((b"\xff\xfe", b"\xfe\xff")) else "utf-8-sig"
        text = content.decode(encoding)
        truncated = len(text) > MAX_CHARS
        for number, line in enumerate(text[:MAX_CHARS].splitlines(), 1):
            if line.strip():
                units.append({"location": f"Line {number}", "text": line.strip(),
                              "source_ref": {"format": "txt", "line": number}})
    elif extension == ".docx":
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            _check_archive(archive)
            root = _xml(archive, "word/document.xml")
        ns = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
        if root.tag != ns + "document":
            raise ValueError("Invalid document")
        chars = 0
        row_refs = {}
        for table_number, table in enumerate(root.iter(ns + "tbl"), 1):
            for row_number, row in enumerate(table.findall(ns + "tr"), 1):
                row_refs[id(row)] = {"format": "docx", "table": table_number, "row": row_number}
        table_paragraphs = {id(p) for row in root.iter(ns + "tr") for p in row.iter(ns + "p")}
        blocks = [node for node in root.iter() if node.tag == ns + "tr"
                  or (node.tag == ns + "p" and id(node) not in table_paragraphs)]
        paragraph_number = 0
        for number, paragraph in enumerate(blocks, 1):
            # Preserve table cell text, tabs and line breaks as original evidence.
            def block_text(block):
                def fragments(node):
                    if node.tag == ns + "tbl":
                        return
                    if node.tag == ns + "t":
                        yield node.text or ""
                    elif node.tag in {ns + "tab", ns + "br"}:
                        yield "\t" if node.tag == ns + "tab" else "\n"
                    else:
                        for child in node:
                            yield from fragments(child)
                return "".join(fragments(block))
            if paragraph.tag == ns + "tr":
                reference = row_refs.get(id(paragraph), {"format": "docx"})
                cells = [(index, block_text(cell)) for index, cell in enumerate(paragraph.findall(ns + "tc"), 1)]
                reference["cells"] = [index for index, _ in cells]
                unit = _row_unit(f"Table row {number}", reference, cells)
            else:
                paragraph_number += 1
                unit = {"location": f"Paragraph {number}", "text": block_text(paragraph).strip(),
                        "source_ref": {"format": "docx", "paragraph": paragraph_number}}
            text = unit["text"]
            if text.strip():
                units.append(unit)
                chars += len(text)
            if chars >= MAX_CHARS or len(units) >= MAX_UNITS:
                truncated = True
                break
    elif extension == ".pdf":
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(content))
        if reader.is_encrypted:
            return {"status": "encrypted"}
        truncated = len(reader.pages) > MAX_PAGES
        chars = 0
        for number, page in enumerate(reader.pages[:MAX_PAGES], 1):
            text = page.extract_text() or ""
            units.append({"location": f"Page {number}", "text": text,
                          "source_ref": {"format": "pdf", "page": number}})
            chars += len(text)
            if chars >= MAX_CHARS:
                truncated = True
                break
    elif extension == ".xlsx":
        units, truncated = _xlsx_units(content)
    else:
        return {"status": "unsupported"}
    return analyse_units(units, truncated)


def extract_document(name: str, content: bytes) -> dict:
    """Parse in a disposable bounded process; return only safe status messages."""
    if Path(name).suffix.lower() not in {".txt", ".pdf", ".docx", ".xlsx"}:
        return {"status": "unsupported"}
    if not content or len(content) > MAX_FILE_BYTES:
        return {"status": "limit"}
    payload = json.dumps({"name": name, "content": base64.b64encode(content).decode("ascii")})
    try:
        result = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--worker"],
                                input=payload, capture_output=True, text=True, timeout=18)
        if result.returncode != 0:
            return {"status": "error"}
        return json.loads(result.stdout)
    except subprocess.TimeoutExpired:
        return {"status": "timeout"}
    except (OSError, ValueError):
        return {"status": "error"}


if __name__ == "__main__":
    import resource
    resource.setrlimit(resource.RLIMIT_AS, (1024 * 1024 * 1024, 1024 * 1024 * 1024))
    resource.setrlimit(resource.RLIMIT_CPU, (12, 12))
    try:
        request = json.load(sys.stdin)
        output = _extract(request["name"], base64.b64decode(request["content"]))
    except _ExtractionLimit:
        output = {"status": "limit"}
    except _EncryptedArchive:
        output = {"status": "encrypted"}
    except Exception:
        output = {"status": "error"}
    sys.stdout.write(json.dumps(output, ensure_ascii=False))

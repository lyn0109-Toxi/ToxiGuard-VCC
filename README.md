# ToxiGuard VCC — Validation & CMC Review

VCC connects reference concentrations with actual sample preparation values and brings guideline-based validation checks together with CMC document review. Review calculations, adjust rules and acceptance limits, inspect document evidence, and download a combined review memo.

**입력:** 시료 제조값, 시험 결과, 검토 기준, 제품 정보, DMF·CTD 원문·확인값

**결과:** 농도 계산, 밸리데이션 점검, 부족한 근거, 고객 질문, CTD 보완사항, 검토 메모

## Start with the review you need

- **문서 검토 / Document review** — received documents, source excerpts, confirmed values, CTD evidence, P.5.6 rationale, and DMF linkage.
- **계산·밸리데이션 / Calculation and validation** — preparation values, reference concentrations, editable rules and limits, Q14, Q3D, and related-substance PDE/TDI checks.
- **검토 메모 / Review memo** — current inputs, calculations, guideline checks, client questions, and CTD actions in a downloadable memo.

The opening page gives document review and calculation/validation their own direct entry buttons, plus an output preview. Four workspace buttons provide document input, calculation/validation, document/evidence review, and the memo. All nine detailed screens remain available in the sidebar. Korean is the default; English remains available from the first screen and via `?lang=en`.

## Examples and session behavior

This is an editable prototype **started from example data**, including the Naltrexone product profile, document statuses, specification values, and test results. It does not start an empty production project. Replace examples with project evidence before relying on the draft. Sample provenance is shown in the workspace and exported memo.

Native navigation preserves the current session. Product context, saved source tables, calculation inputs, and review data survive page and language changes. The app does not provide a persistent project store: download the memo before refreshing or ending the session.

Readiness scores and review gates are internal rule-based summaries of user inputs. They are not regulatory assessments, compliance certification, or approval probabilities. The app does not upload or automatically read PDF documents and does not generate AI conclusions.

## Detailed review tools

- Client CTD intake and product context
- DMF / CTD source excerpts, confirmed values, and editable document application logic
- CTD 3.2.S / 3.2.P evidence map
- P.5.6 specification rationale and DMF-to-drug-product linkage
- Sample preparation and validation checks by test item
- Editable validation results, rules (`between`, `gte`, `lte`, `info`), and acceptance limits
- Existing Q14 checklist status, related-substance PDE/TDI concentration application, and Q3D route / Core 7 / Full 24 / individual PDE checks
- Client questions, CTD update directions, and downloadable review memo

Calculation logic and regulatory reference tables are unchanged by this interface update. Native navigation replaces full-page links; Korean table headers have unique reverse mappings, and the validation extension is applied once per imported app module.

## Run Locally

```bash
python3 -m pip install -r requirements.txt
python3 -m streamlit run streamlit_app.py --server.port 8518
```

Then open:

```text
http://localhost:8518
```

## GitHub Target

Suggested repository name:

```text
lyn0109-Toxi/ToxiGuard-VCC
```

This folder is GitHub-ready. For exact publish commands, see `GITHUB_PUBLISH.md`.

Streamlit Cloud entrypoint:

```text
streamlit_app.py
```

## Validate

```bash
python3 scripts/validate_calculations.py
python3 scripts/validate_ver3.py
```

The validation suite also exercises edited acceptance criteria and Q14 status, Q3D scope / route / dose / individual PDE, and PDE/TDI concentration application across page and test-item changes.

## Boundary

This is a decision-support prototype. It does not replace expert CMC, regulatory, analytical, toxicology, clinical, legal, or quality review.

## Telmisartan × NORA case study

The landing page and detailed view selector include the isolated Telmisartan
case (`?enter=1&page=case&case=telmisartan&strategy=dual`). Import a NORA case
JSON to preserve edited commercial assumptions; the link alone opens defaults.
The packet is size-limited, validated for strategy/period/region/currency, and
recalculated rather than trusting embedded results.

Document reviews start unverified and experimental results are blank. Editable
preparation examples reuse `calculate_sample_prep`; result/limit examples reuse
`evaluate_rule`. Preparation Pass does not establish method validation. Case
records are separate from the existing project's profiles and tables.

The model and source snapshot match NORA. Configure `NORA_APP_URL` for a local
paired preview; the default public return link needs the corresponding NORA
update. Run `python scripts/validate_telmisartan.py` in addition to the existing
checks. Inputs remain session-scoped; export the memo or JSON before leaving.

## Customer DMF / CTD file receipt

Open **자료 입력 → 섹션별 파일 접수** (or the same tab in source-document
input). Select a section and register one or more PDF, DOCX, XLSX, TXT, DOC or
XLS files. A combined document can be explicitly linked to several sections.
The inventory covers DMF administrative access and S.1–S.7; CTD 1, 2,
3.2.S.1–S.7, 3.2.P.1–P.8, 4 and 5. This supported catalog is not a complete
submission checklist or a determination of applicability. CTD section names
follow the [ICH CTD organization](https://admin.ich.org/page/ctd) and
[M4Q quality sections](https://database.ich.org/sites/default/files/M4Q_Q%26As_R1_Q%26As.pdf).

Sections with no registered file display **정보없음**. File receipt starts as
**검토대기** and does not establish content review, Ready/Verified evidence,
guideline compliance or validation completion. Existing examples, source
excerpts, calculation inputs and review tables remain separate. Registering,
reassigning or removing a file never calls the evidence-application action.

**추가자료 요청** automatically lists missing sections and allows a reviewer to
add clarification requests, owners, due dates and priorities. Marking a section
**해당없음** requires an explanation in the UI and removes it from requests.
Download the CSV request list or customer request document; the combined review
memo also contains the actual file inventory and requests. No messages are sent
to customers automatically.

Files are held only in the current Streamlit session on the VCC server, with no
application disk write, shared cache or external extraction service. They may
be lost on refresh, disconnect or restart. Keep original documents separately;
request exports and the review memo do not contain the original files. Limits
are 20 MiB per file, 100 MiB and 50 unique files per session. Signature/container
checks are format checks, not malware scanning or document-content validation.
Identical bytes are stored once and their section links are combined.

Run the existing checks plus:

```bash
python scripts/validate_document_intake.py
python scripts/validate_document_upload_ui.py
```

These use synthetic documents to check receipt/request transitions, file
limits, CSV escaping, section reassignment/removal, atomic batch registration,
language/page persistence and isolation from existing review data.

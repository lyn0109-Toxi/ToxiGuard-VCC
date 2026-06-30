# ToxiGuard Platform Ver.3

`ToxiGuard Platform Ver.3` is a Streamlit CMC RA Evidence Workbench for consultant-led CTD 3.2.P review.

It is isolated from the existing CTI, SOP Gate, Revenue, and static web apps.

## Core Flow

1. `Client CTD Intake`
2. `Dashboard`
3. `3.2.P Evidence Map`
4. `P.5.6 Specification Rationale`
5. `DMF-to-DP Bridge`
6. `Calculation / Validation Review`
7. `CMC RA Response Memo`
8. `App Launcher`

The consultant meeting workflow is:

```text
Document received -> Input -> Gap/risk summary -> Client question list -> CTD update direction
```

## What Is Included

- Full-screen ToxiGuard Platform landing image that enters the app on click
- Korean / English screen switch
- Product profile sidebar
- Consultant-first `Client CTD Intake` screen
- DMF / LoA, API potency and water, impurity bridge, DP manufacturing, specification, method validation, stability, and CCS intake checklist
- Intake readiness score based on document receipt, usability, and risk
- Client meeting summary generated from received CTD/DMF information
- Client question list generated from intake gaps and high-risk areas
- CTD update direction mapped to target CTD sections
- P.1-P.8 evidence map with source, owner, risk, and next action
- P.5.6 specification rationale table
- DMF-to-DP bridge table
- Sample preparation concentration check with actual weighing, stock volume, aliquot, final volume, and dilution factor
- LOD / LOQ as % of reference concentration
- Linearity R2 and intercept risk warning
- Validation result gate table
- CMC RA Decision Packet preview with Client CTD Intake Snapshot and Markdown download
- App launcher for SOP Gate, CTI, and Revenue modules

## Run Locally

```bash
cd /Users/leeyoung-nam/Desktop/ToxiGuard/ToxiGuard-Platform-Ver3
bash run_streamlit.sh
```

Then open:

```text
http://localhost:8507
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
cd /Users/leeyoung-nam/Desktop/ToxiGuard/ToxiGuard-Platform-Ver3
python3 scripts/validate_ver3.py
```

## Boundary

This is a decision-support prototype. It does not replace expert CMC, regulatory, analytical, toxicology, clinical, legal, or quality review.

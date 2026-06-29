# ToxiGuard Platform Ver.3

`ToxiGuard Platform Ver.3` is a Streamlit CMC RA Evidence Workbench focused on CTD 3.2.P.

It is isolated from the existing CTI, SOP Gate, Revenue, and static web apps.

## Core Flow

1. `3.2.P Evidence Map`
2. `P.5.6 Specification Rationale`
3. `DMF-to-DP Bridge`
4. `Calculation / Validation Review`
5. `CMC RA Response Memo`

## What Is Included

- Full-screen ToxiGuard Platform landing image that enters the app on click
- Korean / English screen switch
- Product profile sidebar
- P.1-P.8 evidence map with source, owner, risk, and next action
- P.5.6 specification rationale table
- DMF-to-DP bridge table
- Sample preparation concentration check with actual weighing, stock volume, aliquot, final volume, and dilution factor
- LOD / LOQ as % of reference concentration
- Linearity R2 and intercept risk warning
- Validation result gate table
- CMC RA Decision Packet preview and Markdown download
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

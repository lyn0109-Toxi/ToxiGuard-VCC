# ToxiGuard Platform Ver.3

`ToxiGuard Platform Ver.3` is a Streamlit CMC RA Evidence Workbench for consultant-led DMF, CTD 3.2.S, and CTD 3.2.P review.

It is isolated from the existing CTI, SOP Gate, Revenue, and static web apps.

## Core Flow

1. `Client CTD Intake`
2. `Document Input`
3. `Dashboard`
4. `3.2.S / 3.2.P Evidence Map`
5. `P.5.6 Specification Rationale`
6. `DMF-to-DP Bridge`
7. `Calculation / Validation Review`
8. `CMC RA Response Memo`
9. `App Launcher`

The consultant meeting workflow is:

```text
Document received -> Source text / confirmed value -> Key CMC decision point -> Gap/risk summary -> Client question list -> CTD update direction
```

## What Is Included

- Full-screen ToxiGuard Platform landing image that enters the app on click
- Korean / English screen switch
- Product profile sidebar with API, DMF holder, formulation platform, clinical material, and target-region fields
- Consultant-first `Client CTD Intake` screen
- Editable `Document Input` workspace for DMF source text, CTD 3.2.S, CTD 3.2.P, and other CTD modules
- Editable company document application logic that defines how raw material, DMF, formulation, process, specification, stability, clinical material, and regional documents are used in CMC judgement
- Key Decision Points board that converts document gaps and high-risk inputs into user-reviewable CMC judgement prompts, affected CTD sections, evidence requirements, and suggested actions
- Apply Document Inputs action that pushes edited DMF/CTD source inputs into the Evidence Map, DMF-to-DP Bridge, and P.5.6 rationale risk seed
- Product-profile-driven review prompts reflected in Dashboard and Evidence Map
- DMF / LoA, API potency and water, impurity bridge, DP manufacturing, specification, method validation, stability, and CCS intake checklist
- Intake readiness score based on document receipt, usability, and risk
- Client meeting summary generated from received CTD/DMF information
- Client question list generated from intake gaps and high-risk areas
- CTD update direction mapped to target CTD sections
- 3.2.S and 3.2.P evidence maps with source, owner, risk, and next action
- P.5.6 specification rationale table
- DMF-to-DP bridge table
- Test-specific validation review for assay, related substances, dissolution, elemental impurities, and nitrosamines
- ICH Q14 analytical procedure development check for ATP, matrix definition, technology selection, calibration/range, critical parameters, robustness, control strategy, lifecycle change, and transfer comparability
- ICH Q3D elemental impurity scope review with Core 7 (Class 1 + Class 2A) and Full 24 element modes
- PDE/TDI-based limit calculation for related substances and elemental impurities using MDD, route, and ICH threshold logic
- Sample preparation concentration check with actual weighing, stock volume, aliquot, final volume, and dilution factor by test item
- LOD / LOQ as % of reference concentration
- Linearity R2 and intercept risk warning
- Test-specific validation result gate tables and overall review summary
- ICH M14 safety-evidence note separated from analytical validation bases such as ICH Q2(R2), Q14, Q3D(R2), and M7(R2)
- CMC RA Decision Packet preview with product profile, document application logic, key decision points, DMF/CTD source input snapshots, Client CTD Intake Snapshot, and Markdown download
- App launcher for SOP Gate, CTI, Revenue, and ToxiGuard-MediLens medication safety modules

## Run Locally

```bash
cd /Users/leeyoung-nam/Desktop/ToxiGuard/Github/ToxiGuard-Platform-Ver3
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
cd /Users/leeyoung-nam/Desktop/ToxiGuard/Github/ToxiGuard-Platform-Ver3
python3 scripts/validate_ver3.py
```

## Boundary

This is a decision-support prototype. It does not replace expert CMC, regulatory, analytical, toxicology, clinical, legal, or quality review.

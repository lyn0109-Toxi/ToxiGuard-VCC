"""Presentation-only process diagrams; calculation values come from the core."""
from html import escape
from typing import Any

from analytical_workspace import label

UI_BUILD = "analytical-design-2026-10-11-v2"

STYLE = """
<style>
:root {--vcc-ink:#203942; --vcc-muted:#61737b; --vcc-line:#dbe4e6; --vcc-accent:#315e70;}
[data-testid="stAppViewContainer"] {background:#f6f8f9;}
[data-testid="stSidebar"] {background:#edf2f4; border-right:1px solid #dbe4e6;}
.block-container {max-width:1260px; padding-top:3.8rem;}
.tg-app-hero {min-height:0!important; box-shadow:none!important; margin-bottom:8px!important; border-radius:14px!important;}
.tg-app-hero-inner {min-height:0!important; padding:18px 24px!important;}
.tg-app-hero h1 {font-size:1.35rem!important; line-height:1.3!important; margin:0!important; color:#fff!important;}
.tg-app-hero p {display:none;}
.tg-eyebrow {font-size:.65rem!important; letter-spacing:.09em; color:#b7d3de!important; margin-bottom:5px!important;}
.st-key-vcc_workflow button {white-space:normal; height:auto; min-height:40px; font-size:.8rem; line-height:1.35;}
.st-key-vcc_workflow {margin-bottom:8px;}
.am-heading {padding:10px 0 14px;}
.am-kicker {font-size:.7rem; font-weight:700; letter-spacing:.12em; color:#617b88; margin-bottom:7px;}
.am-heading h2 {font-size:clamp(1.65rem,2.5vw,2.1rem); line-height:1.25; letter-spacing:-.035em; color:var(--vcc-ink); margin:0 0 9px; padding:0;}
.am-heading p {font-size:.94rem; line-height:1.65; color:var(--vcc-muted); margin:0; max-width:780px;}
.am-legend {display:flex; flex-wrap:wrap; gap:8px; margin-top:14px;}
.am-tag {border:1px solid #d7e1e5; background:#fff; color:#526a75; border-radius:6px; padding:4px 9px; font-size:.72rem; line-height:1.5;}
.am-tag.source {background:#edf3f8; color:#355d7a;}
.am-tag.calc {background:#edf1f2; color:#304e59;}
.am-section {display:flex; gap:12px; align-items:flex-start; padding:17px 0 10px;}
.am-section b {display:grid; place-items:center; width:30px; height:30px; flex:0 0 30px; background:#e6eef2; color:#315e70; border-radius:8px; font-size:.76rem;}
.am-section h3 {font-size:1.15rem; line-height:1.45; padding:0; margin:0 0 3px; color:var(--vcc-ink);}
.am-section p {margin:0; font-size:.83rem; color:var(--vcc-muted); line-height:1.65;}
.am-status-grid {display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:10px; margin:8px 0 18px;}
.am-status {padding:14px 16px; border:1px solid var(--vcc-line); border-radius:10px; background:#fff; min-width:0;}
.am-status small {display:block; color:var(--vcc-muted); font-size:.73rem; margin-bottom:5px;}
.am-status strong {display:block; color:#365360; font-size:.9rem; line-height:1.5;}
.am-status span {display:block; color:var(--vcc-muted); font-size:.75rem; margin-top:4px; line-height:1.5;}
.am-missing {border-left:3px solid #b68a40; background:#fbf6ec; border-radius:0 8px 8px 0; padding:12px 15px; color:#6d532c; font-size:.85rem; line-height:1.65; margin:8px 0 15px; overflow-wrap:anywhere;}
.am-flow {display:flex; flex-direction:column; gap:14px; margin:8px 0 18px;}
.am-node {position:relative; min-width:0; border:1px solid var(--vcc-line); border-radius:10px; padding:11px 14px 11px 48px; background:#fff;}
.am-node:not(:last-child)::after {content:'↓'; position:absolute; right:50%; bottom:-17px; color:#6b8591; font-size:1rem; z-index:1;}
.am-node.final {border-color:#9bb2be; background:#edf3f6;}
.am-node svg {width:23px; height:23px; color:#587c8d; position:absolute; left:14px; top:17px;}
.am-node small {font-size:.72rem; color:#61737b; display:block; line-height:1.5;}
.am-node strong {display:block; font-size:.94rem; color:#203942; margin:4px 0; line-height:1.45; overflow-wrap:anywhere;}
.am-node span {font-size:.75rem; line-height:1.5; color:#61737b; display:block;}
[data-testid="stVerticalBlockBorderWrapper"] {border-color:#dbe4e6; border-radius:12px; background:#fff;}
[data-testid="stWidgetLabel"] p {font-size:.82rem; color:#415761;}
[data-testid="stTextInput"] input,[data-testid="stNumberInput"] input {font-variant-numeric:tabular-nums;}
[data-testid="stMetricLabel"] p {font-size:.76rem; white-space:normal;}
[data-testid="stMetricValue"] {font-size:1.4rem; color:#294955; font-variant-numeric:tabular-nums;}
[data-testid="stTabs"] [role="tablist"] {gap:8px; border-bottom:1px solid #dbe4e6;}
[data-testid="stTabs"] [role="tab"] {padding:9px 12px; height:auto; font-size:.85rem;}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {background:#e8eff3; color:#294f62; border-radius:8px 8px 0 0;}
@media(max-width:760px) {
 .am-status-grid {grid-template-columns:1fr; gap:7px;}
 .am-status {padding:11px 13px;}
 .am-flow {flex-direction:column; gap:14px;}
 .am-node {flex:0 0 auto; padding:12px 14px 12px 48px;}
 .am-node svg {position:absolute; left:14px; top:17px;}
 .am-node:not(:last-child)::after {content:'↓'; top:auto; bottom:-17px; right:50%;}
 .am-heading h2 {font-size:1.55rem;}
 .tg-app-hero-inner {padding:14px 18px!important;}
 .st-key-vcc_workflow [data-testid="stHorizontalBlock"] {flex-wrap:wrap; gap:6px;}
 .st-key-vcc_workflow [data-testid="stColumn"] {min-width:calc(33.33% - 8px)!important; flex:1 1 30%!important; width:auto!important;}
 [data-testid="stTabs"] [role="tablist"] {overflow-x:auto;}
 [data-testid="stTabs"] [role="tab"] {white-space:nowrap; flex:0 0 auto;}
}
</style>
"""

def section_html(number: str, title: str, detail: str = "") -> str:
    return f'<div class="am-section"><b>{escape(number)}</b><div><h3>{escape(title)}</h3><p>{escape(detail)}</p></div></div>'

def status_html(items: list[tuple[str, str, str]]) -> str:
    return '<div class="am-status-grid">' + ''.join(f'<article class="am-status"><small>{escape(title)}</small><strong>{escape(value)}</strong><span>{escape(detail)}</span></article>' for title, value, detail in items) + '</div>'

def missing_preparation(prep: dict[str, Any], product: dict[str, Any], reference: bool) -> list[str]:
    fields = ["amount", "basis_factor", "stock_ml"]
    if not reference:
        fields.append("extraction")
    if prep["correction_mode"] != "none":
        fields.append("potency")
    if prep["correction_mode"] == "dry":
        fields.append("water")
    missing = [field for field in fields if prep.get(field) is None]
    if prep["basis"] in {"product_mass", "product_volume"}:
        missing += [field for field in ("strength", "whole_unit") if product.get(field) is None]
    for step in prep.get("steps", []):
        missing += [field for field in ("aliquot_ml", "final_ml") if step.get(field) is None]
    return list(dict.fromkeys(missing))

def flow_html(prep: dict[str, Any], calc: dict[str, Any] | None, lang: str) -> str:
    """No intermediate concentration is displayed until the core validates every step."""
    ko = lang == "ko"
    def word(en: str, kr: str) -> str:
        return kr if ko else en
    def fmt(value: Any, unit: str) -> str:
        return word("Unknown", "미확인") if value is None else f"{value:.12g} {unit}"
    flask = '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M9 3h6M10 3v6l-5 9a2 2 0 0 0 2 3h10a2 2 0 0 0 2-3l-5-9V3M8 15h8"/></svg>'
    original_detail = label(prep["basis"], lang)
    if calc:
        original_detail += " · " + word("nominal analyte ", "명목 분석대상 ") + fmt(calc["nominal_mg"], "mg") + " · " + word("corrected ", "보정 후 ") + fmt(calc["corrected_mg"], "mg")
    nodes = [(word("Original amount", "원래 채취량"), fmt(prep.get("amount"), prep["amount_unit"]), original_detail, False),
             (word("Stock solution", "원액"), fmt(prep.get("stock_ml"), "mL"), fmt(calc["stock_ug_ml"], "µg/mL") if calc else word("Concentration pending", "농도 계산 대기"), False)]
    for index, step in enumerate(prep.get("steps", []), 1):
        concentration = calc["steps"][index-1]["concentration_ug_ml"] if calc else None
        nodes.append((word(f"Dilution {index}", f"희석 {index}"), f'{fmt(step.get("aliquot_ml"), "mL")} → {fmt(step.get("final_ml"), "mL")}', fmt(concentration, "µg/mL") if calc else word("Concentration pending", "농도 계산 대기"), False))
    nodes.append((word("Final concentration", "최종 농도"), fmt(calc["final_ug_ml"], "µg/mL") if calc else word("Not calculated", "계산 미완료"), word("Calculated · review separate", "계산값 · 검토 상태 별도") if calc else word("Complete missing inputs", "누락 입력 확인 필요"), True))
    return '<div class="am-flow">' + ''.join(f'<article class="am-node{" final" if final else ""}">{flask}<small>{escape(title)}</small><strong>{escape(value)}</strong><span>{escape(detail)}</span></article>' for title, value, detail, final in nodes) + '</div>'

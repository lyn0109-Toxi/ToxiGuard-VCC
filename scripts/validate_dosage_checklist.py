"""Synthetic scope, reviewer-state, export and UI regressions for dosage checklists."""
from __future__ import annotations

import copy
from datetime import date
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from streamlit.testing.v1 import AppTest

from dosage_checklist import (STATE_KEY, checklist_report, configure_scope, item_rows,
                              new_state, profile_key, scope_items, suggest_template, update_item)


ORAL = {"product": "Synthetic tablet", "active_substance": "Synthetic API",
        "dosage": "Tablet", "route": "Oral", "strength": "20 mg", "batch": "B01"}
STERILE = {**ORAL, "product": "Synthetic injection", "dosage": "Injection", "route": "Intramuscular"}
UNKNOWN = {"product": "Synthetic unknown product", "dosage": "", "route": ""}


def confirmed(profile=ORAL, template="oral_nonsterile"):
    return configure_scope(new_state(profile), template, True)


def ui(profile=ORAL, lang="en"):
    code = f"""
import sys
sys.path.insert(0, {str(ROOT)!r})
import streamlit as st
from dosage_checklist import render_checklist
st.session_state.setdefault('fixture_profile', {profile!r})
st.session_state.setdefault('fixture_lang', {lang!r})
st.session_state.setdefault('evidence_df', [{{'Status': 'Example partial'}}])
st.session_state.setdefault('validation_df', [{{'Result': 98.5}}])
render_checklist(st.session_state.fixture_lang, st.session_state.fixture_profile)
"""
    return AppTest.from_string(code, default_timeout=15).run()


def click(page, label):
    matches = [button for button in page.button if button.label == label]
    assert len(matches) == 1, label
    return matches[0].click().run()


class ChecklistTests(unittest.TestCase):
    def test_scope_suggestions_are_unconfirmed_and_conflicts_stay_unknown(self):
        self.assertEqual(suggest_template(ORAL), "oral_nonsterile")
        self.assertEqual(suggest_template(STERILE), "sterile")
        self.assertEqual(suggest_template({"dosage": "경구 비무균 정제"}), "oral_nonsterile")
        self.assertEqual(suggest_template({"dosage": "Non-sterile oral solution"}), "oral_nonsterile")
        self.assertEqual(suggest_template({"dosage": "Oral tablet / sterile injection"}), "")
        self.assertEqual(suggest_template(UNKNOWN), "")
        self.assertFalse(new_state(ORAL)["confirmed"])
        self.assertTrue(all(row["status"] == "unconfirmed" for row in item_rows(new_state(ORAL))))

    def test_oral_excludes_sterile_specific_items(self):
        oral_ids = {item[0] for item in scope_items("oral_nonsterile")}
        self.assertTrue({"sterility_assurance", "endotoxin", "container_integrity"}.isdisjoint(oral_ids))
        self.assertIn("oral_microbiology", oral_ids)
        sterile_ids = {item[0] for item in scope_items("sterile")}
        self.assertTrue({"sterility_assurance", "endotoxin", "container_integrity"}.issubset(sterile_ids))
        with self.assertRaises(ValueError):
            update_item(confirmed(), "endotoxin")

    def test_explicit_review_and_na_requirements(self):
        original = new_state(ORAL)
        with self.assertRaises(ValueError):
            update_item(original, "product_context")
        state = confirmed()
        for arguments in ({"status": "not_applicable", "reason": "  "},
                          {"status": "reviewed", "note": "Reviewed", "source": ""},
                          {"status": "reviewed", "source": "CTD p. 1", "note": ""},
                          {"status": "automatic_pass"}, {"due_date": "not-a-date"}):
            with self.assertRaises(ValueError):
                update_item(state, "product_context", **arguments)
        updated = update_item(state, "oral_release", "not_applicable", reason="Not a solid product",
                              owner="Reviewer A", due_date=date(2030, 1, 15))
        self.assertEqual(updated["records"]["oral_release"]["due_date"], "2030-01-15")
        self.assertEqual(state["records"], {})

    def test_scope_switch_exports_only_active_items(self):
        state = configure_scope(new_state(ORAL), "sterile", True)
        state = update_item(state, "endotoxin", "reviewed", source="Synthetic report v2, p. 8, table 2",
                            note="Reviewer checked product-specific applicability")
        state = configure_scope(state, "oral_nonsterile", True)
        report = checklist_report(ORAL, state=state)
        self.assertNotIn("Synthetic report v2", report)
        self.assertNotIn("Endotoxin/pyrogen", report)
        self.assertEqual(state["records"]["endotoxin"]["status"], "reviewed")
        self.assertTrue(all(row["status"] == "unconfirmed" for row in item_rows(state)))

    def test_profile_and_batch_context_isolation(self):
        state = update_item(confirmed(), "product_context", "reviewed", source="Synthetic CTD v2, p. 1",
                            note="Identity and B01 checked")
        self.assertNotEqual(profile_key(ORAL), profile_key({**ORAL, "batch": "B02"}))
        self.assertNotEqual(profile_key(ORAL), profile_key({**ORAL, "strength": "40 mg"}))
        self.assertNotEqual(profile_key(ORAL), profile_key({**ORAL, "dosage": "Injection"}))
        with self.assertRaises(ValueError):
            checklist_report(STERILE, state=state)
        self.assertIn("Review batch: B01", checklist_report(ORAL, state=state))

    def test_export_keeps_customer_text_and_scope_disclaimer(self):
        state = update_item(confirmed(), "document_versions", "unconfirmed", source="Method v2 | p. 4",
                            note="Need <source>\nConfirm effective date", owner="QC reviewer")
        report = checklist_report(ORAL, state=state)
        self.assertIn("Method v2 \\| p. 4", report)
        self.assertIn("&lt;source&gt;<br>", report)
        self.assertIn("not an automated compliance", report)
        self.assertIn("QC reviewer", report)
        self.assertIn("범위 미확인", checklist_report(ORAL, "ko", new_state(ORAL)))

    def test_ui_scope_gate_and_na_validation_without_evidence_mutation(self):
        page = ui()
        self.assertFalse(page.exception)
        prefix = "dosage_check_" + profile_key(ORAL)
        before = {key: copy.deepcopy(page.session_state[key]) for key in ("evidence_df", "validation_df")}
        self.assertFalse(any(widget.label == "Review item to record" for widget in page.selectbox))
        page.checkbox(key=prefix + "_confirmed").check()
        click(page, "Save review scope")
        self.assertFalse(page.exception)
        page.selectbox(key=prefix + "_item_oral_nonsterile").select("oral_release").run()
        item_prefix = prefix + "_oral_release"
        page.selectbox(key=item_prefix + "_status").select("not_applicable")
        click(page, "Save item record")
        self.assertTrue(page.error)
        self.assertNotIn("oral_release", page.session_state[STATE_KEY][profile_key(ORAL)]["records"])
        page.text_area(key=item_prefix + "_reason").input("Synthetic product-specific rationale")
        page.text_input(key=item_prefix + "_owner").input("Reviewer A")
        page.date_input(key=item_prefix + "_due").set_value(date(2030, 1, 15))
        click(page, "Save item record")
        self.assertFalse(page.exception)
        record = page.session_state[STATE_KEY][profile_key(ORAL)]["records"]["oral_release"]
        self.assertEqual(record["status"], "not_applicable")
        self.assertEqual(record["owner"], "Reviewer A")
        self.assertEqual(record["due_date"], "2030-01-15")
        for key, value in before.items():
            self.assertEqual(value, page.session_state[key])
        page.session_state["fixture_lang"] = "ko"
        page.run()
        self.assertFalse(page.exception)
        self.assertEqual(page.session_state[STATE_KEY][profile_key(ORAL)]["records"]["oral_release"], record)

    def test_ui_unknown_profile_requires_choice_and_sessions_are_isolated(self):
        unknown_page = ui(UNKNOWN)
        prefix = "dosage_check_" + profile_key(UNKNOWN)
        self.assertFalse(unknown_page.exception)
        self.assertEqual(unknown_page.selectbox(key=prefix + "_scope").value, "")
        unknown_page.checkbox(key=prefix + "_confirmed").check()
        click(unknown_page, "Save review scope")
        self.assertTrue(unknown_page.error)
        unknown_page.selectbox(key=prefix + "_scope").select("other")
        click(unknown_page, "Save review scope")
        self.assertFalse(unknown_page.exception)
        self.assertTrue(unknown_page.session_state[STATE_KEY][profile_key(UNKNOWN)]["confirmed"])
        first = ui()
        second = ui()
        context = profile_key(ORAL)
        first.session_state[STATE_KEY][context] = update_item(confirmed(), "document_versions", "unconfirmed", note="Session one only")
        second.run()
        self.assertEqual(second.session_state[STATE_KEY][context]["records"], {})
        first.session_state["fixture_profile"] = {**ORAL, "batch": "B02"}
        first.run()
        other_context = profile_key({**ORAL, "batch": "B02"})
        self.assertFalse(first.session_state[STATE_KEY][other_context]["confirmed"])
        self.assertEqual(first.session_state[STATE_KEY][other_context]["records"], {})
        self.assertIn("document_versions", first.session_state[STATE_KEY][context]["records"])


if __name__ == "__main__":
    unittest.main(verbosity=2)

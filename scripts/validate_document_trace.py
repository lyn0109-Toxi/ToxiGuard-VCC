"""Version/provenance regressions with synthetic documents only."""
import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from document_trace import applicability, compare_documents, new_trace, prune_trace, save_document, save_evidence, trace_report
from document_intake import add_file, new_intake
from streamlit.testing.v1 import AppTest

META = dict(version='LIMS v2', system='LIMS', source='METHOD-001', product='Product A', batch='B001', stage='Response', reviewer='Reviewer A', status='confirmed')
CANDIDATE = dict(topic='specification', location='Page 2', source_ref={'format': 'pdf', 'page': 2}, excerpt='Assay: 98-102%')
REVIEW = dict(status='confirmed', confirmed_value='98-102%', reviewer='Reviewer A', ctd_target='3.2.P.5.1', request='Provide approved method.', owner='QC', due_date='2030-01-02')


class TraceTests(unittest.TestCase):
    def test_confirmation_requires_metadata(self):
        with self.assertRaises(ValueError):
            save_document(new_trace(), 'file', {'status': 'confirmed'})
        with self.assertRaises(ValueError):
            save_evidence(new_trace(), 'file', CANDIDATE, REVIEW)

    def test_scope_product_batch_stage(self):
        document = save_document(new_trace(), 'file', META)['documents']['file']
        self.assertEqual(applicability(document, 'Product A', 'B001', 'Response'), 'confirmed')
        for product, batch, stage in [('Other', 'B001', 'Response'), ('Product A', 'B002', 'Response'), ('Product A', 'B001', 'Final approval')]:
            self.assertEqual(applicability(document, product, batch, stage), 'scope_mismatch')
        self.assertEqual(applicability(document, 'Product A'), 'unconfirmed')

    def test_metadata_change_invalidates_evidence(self):
        trace = save_document(new_trace(), 'file', META)
        trace = save_evidence(trace, 'file', CANDIDATE, REVIEW)
        original = copy.deepcopy(trace)
        updated = save_document(trace, 'file', {**META, 'version': 'QC RDM v3'})
        self.assertEqual(updated['evidence'][0]['status'], 'unconfirmed')
        self.assertEqual(updated['evidence'][0]['document_snapshot']['version'], 'LIMS v2')
        self.assertEqual(trace, original)

    def test_edit_record_and_prune(self):
        trace = save_document(new_trace(), 'file', META)
        trace = save_evidence(trace, 'file', CANDIDATE, REVIEW)
        trace = save_evidence(trace, 'file', CANDIDATE, {**REVIEW, 'owner': 'RA'})
        self.assertEqual(len(trace['evidence']), 1)
        self.assertEqual(trace['evidence'][0]['owner'], 'RA')
        self.assertEqual(prune_trace(trace, {}), new_trace())

    def test_confirmation_withdrawal_invalidates_evidence(self):
        trace = save_evidence(save_document(new_trace(), 'file', META), 'file', CANDIDATE, REVIEW)
        for status in ['unconfirmed', 'conflicting']:
            updated = save_document(trace, 'file', {**META, 'status': status})
            self.assertEqual(updated['evidence'][0]['status'], 'unconfirmed')
            self.assertIn('confirmation changed', updated['evidence'][0]['invalidation'])

    def test_version_diff_and_bounds(self):
        old = {'status': 'ok', 'units': [{'location': 'Page 1', 'text': 'Assay 95-105%\nOld method'}]}
        new = {'status': 'ok', 'units': [{'location': 'Page 2', 'text': 'Assay 98-102%\nNew method'}]}
        diff = compare_documents(old, new)
        self.assertEqual(diff['changes'][0]['change'], 'replace')
        self.assertEqual(diff['changes'][0]['old'][0]['location'], 'Page 1')
        self.assertEqual(diff['changes'][0]['new'][0]['location'], 'Page 2')
        self.assertFalse(diff['partial'])
        self.assertFalse(compare_documents(old, old)['changes'])
        self.assertTrue(compare_documents(old, {**new, 'truncated': True})['partial'])
        with self.assertRaises(ValueError):
            compare_documents(old, {'status': 'empty'})

    def test_report_preserves_actions_and_scope(self):
        trace = save_document(new_trace(), 'file', META)
        trace = save_evidence(trace, 'file', CANDIDATE, REVIEW)
        report = trace_report(trace, {'file': {'name': 'source.pdf'}}, profile={'product': 'Product A', 'batch': 'B002', 'stage': 'Response'})
        for fragment in ['scope_mismatch', 'METHOD-001', 'Page 2', 'Provide approved method.', '2030-01-02', 'QC']:
            self.assertIn(fragment, report)

    def test_ui_diff_and_memo(self):
        page = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'streamlit_app.py'), default_timeout=30)
        page.query_params.update({'enter': '1', 'page': 'documents', 'lang': 'en'})
        page.run()
        self.assertFalse(page.exception)
        state = add_file(new_intake(), 'v1.txt', b'Drug substance: Example\nAssay 95-105%', ['CTD.3.2.S.4'])
        state = add_file(state, 'v2.txt', b'Drug substance: Example\nAssay 98-102%', ['CTD.3.2.S.4'])
        ids = list(state['files'])
        page.session_state['customer_document_intake'] = state
        page.session_state['customer_document_trace'] = save_evidence(save_document(new_trace(), ids[1], META), ids[1], CANDIDATE, REVIEW)
        page.run()
        self.assertFalse(page.exception)
        page.selectbox(key='trace_file').set_value(ids[1]).run()
        page.button(key='trace_compare').click().run()
        self.assertFalse(page.exception)
        self.assertTrue(page.session_state['trace_diff']['changes'])
        self.assertTrue(any('98-102%' in block.value for block in page.code))
        page.selectbox(key='detail_page_widget').set_value('response').run()
        self.assertFalse(page.exception)
        memos = [area.value for area in page.text_area if 'METHOD-001' in str(area.value)]
        self.assertEqual(len(memos), 1)
        self.assertIn('2030-01-02', memos[0])


if __name__ == '__main__':
    unittest.main(verbosity=2)

"""Synthetic extraction and UI regressions; no customer documents required."""
import copy
import io
from pathlib import Path
import sys
import unittest
import zipfile
from xml.sax.saxutils import quoteattr

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from document_insights import MAX_ARCHIVE_MEMBERS, MAX_CHARS, MAX_XLSX_CELLS, MAX_XML_BYTES, extract_document
from document_intake import add_file, new_intake
from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject
from streamlit.testing.v1 import AppTest

SOURCE = 'Drug substance: Telmisartan\n3.2.S.4.1 Specification\nAssay acceptance criteria: 98-102%\n3.2.S.7 Stability\nStorage: 25 C\nAnalytical method validation: accuracy and precision\n'


def pdf_bytes(text=None, encrypted=False):
    writer = PdfWriter()
    page = writer.add_blank_page(width=595, height=842)
    if text:
        font = DictionaryObject({NameObject('/Type'): NameObject('/Font'), NameObject('/Subtype'): NameObject('/Type1'), NameObject('/BaseFont'): NameObject('/Helvetica')})
        page[NameObject('/Resources')] = DictionaryObject({NameObject('/Font'): DictionaryObject({NameObject('/F1'): writer._add_object(font)})})
        stream = DecodedStreamObject()
        stream.set_data(('BT /F1 12 Tf 40 780 Td (' + text + ') Tj ET').encode('ascii'))
        page[NameObject('/Contents')] = writer._add_object(stream)
    if encrypted:
        writer.encrypt('synthetic-test-password')
    output = io.BytesIO()
    writer.write(output)
    return output.getvalue()


def docx_bytes(xml):
    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w') as archive:
        archive.writestr('[Content_Types].xml', '<Types/>')
        archive.writestr('word/document.xml', xml)
    return output.getvalue()


def xlsx_bytes(sheet_xml, shared_xml=None, sheet_name='QC Results', relationship=None, extra=None):
    ns = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
    rel = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
    default_relation = f'<Relationship Id="rId1" Type="{rel}/worksheet" Target="worksheets/sheet1.xml"/>'
    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('[Content_Types].xml', '<Types/>')
        archive.writestr('xl/workbook.xml', f'<workbook xmlns="{ns}" xmlns:r="{rel}"><sheets><sheet name={quoteattr(sheet_name)} sheetId="1" r:id="rId1"/></sheets></workbook>')
        archive.writestr('xl/_rels/workbook.xml.rels', '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' + (relationship or default_relation) + '</Relationships>')
        archive.writestr('xl/worksheets/sheet1.xml', sheet_xml)
        if shared_xml is not None:
            archive.writestr('xl/sharedStrings.xml', shared_xml)
        for name, value in (extra or {}).items():
            archive.writestr(name, value)
    return output.getvalue()


def worksheet(rows):
    return '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>' + rows + '</sheetData></worksheet>'


def column_name(number):
    name = ''
    while number:
        number, remainder = divmod(number - 1, 26)
        name = chr(65 + remainder) + name
    return name


class InsightsTests(unittest.TestCase):
    def test_text_evidence_and_topics(self):
        result = extract_document('ctd.txt', SOURCE.encode())
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(result['drugs'][0]['name'], 'Telmisartan')
        self.assertEqual(result['drugs'][0]['location'], 'Line 1')
        self.assertEqual(result['drugs'][0]['source_ref'], {'format': 'txt', 'line': 1})
        self.assertEqual(result['review_status'], 'unconfirmed')
        self.assertEqual(result['drugs'][0]['review_status'], 'unconfirmed')
        self.assertIn('3.2.S.4.1', [s['section'] for s in result['sections']])
        self.assertTrue(next(t for t in result['topics'] if t['key'] == 'stability')['evidence'])
        self.assertEqual(next(t for t in result['topics'] if t['key'] == 'clinical')['matches'], 0)

    def test_korean_utf16(self):
        result = extract_document('ctd.txt', '제품명: 시험약\n3.2.P.5 규격\n불순물 허용기준'.encode('utf-16'))
        self.assertEqual(result['drugs'][0]['name'], '시험약')
        self.assertTrue(next(t for t in result['topics'] if t['key'] == 'impurities')['matches'])

    def test_text_pdf(self):
        result = extract_document('ctd.pdf', pdf_bytes('Drug substance: Telmisartan'))
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(result['drugs'][0]['name'], 'Telmisartan')
        self.assertEqual(result['drugs'][0]['location'], 'Page 1')
        self.assertEqual(result['drugs'][0]['source_ref'], {'format': 'pdf', 'page': 1})

    def test_scan_and_encryption(self):
        self.assertEqual(extract_document('scan.pdf', pdf_bytes())['status'], 'empty')
        self.assertEqual(extract_document('locked.pdf', pdf_bytes(encrypted=True))['status'], 'encrypted')

    def test_docx_table(self):
        xml = '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:tbl><w:tr><w:tc><w:p><w:r><w:t>Drug substance</w:t></w:r></w:p></w:tc><w:tc><w:p><w:r><w:t>Telmisartan</w:t></w:r></w:p></w:tc></w:tr></w:tbl><w:p><w:r><w:t>3.2.S.7 Stability</w:t></w:r></w:p></w:body></w:document>'
        result = extract_document('ctd.docx', docx_bytes(xml))
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(result['drugs'][0]['name'], 'Telmisartan')
        self.assertTrue(result['drugs'][0]['location'].startswith('Table row'))
        self.assertEqual(result['drugs'][0]['source_ref'], {'format': 'docx', 'table': 1, 'row': 1, 'cells': [1, 2]})
        self.assertEqual(result['sections'][0]['location'], 'Paragraph 2')
        self.assertEqual(result['sections'][0]['source_ref'], {'format': 'docx', 'paragraph': 1})

    def test_docx_nested_table_has_its_own_source(self):
        xml = '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:tbl><w:tr><w:tc><w:p><w:r><w:t>Outer row</w:t></w:r></w:p><w:tbl><w:tr><w:tc><w:p><w:r><w:t>3.2.S.7 Stability</w:t></w:r></w:p></w:tc></w:tr></w:tbl></w:tc></w:tr></w:tbl></w:body></w:document>'
        result = extract_document('nested.docx', docx_bytes(xml))
        self.assertEqual(result['sections'][0]['source_ref'], {'format': 'docx', 'table': 2, 'row': 1, 'cells': [1]})
        self.assertEqual(result['units'][0]['text'], 'Outer row')

    def test_xlsx_shared_inline_and_numeric_cells(self):
        shared = '<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><si><t>Drug substance</t></si><si><r><t>Telmi</t></r><r><t>sartan</t></r></si></sst>'
        rows = '<row r="1"><c r="A1" t="s"><v>0</v></c><c r="B1" t="s"><v>1</v></c></row><row r="4"><c r="C4" t="inlineStr"><is><t>3.2.S.4.1 Specification</t></is></c><c r="E4"><v>98</v></c></row>'
        result = extract_document('validation.xlsx', xlsx_bytes(worksheet(rows), shared))
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(result['drugs'][0]['name'], 'Telmisartan')
        self.assertEqual(result['drugs'][0]['source_ref']['sheet'], 'QC Results')
        self.assertEqual(result['drugs'][0]['source_ref']['cells'], ['A1', 'B1'])
        self.assertEqual(result['sections'][0]['source_ref']['cells'], ['C4'])
        self.assertEqual(result['sections'][0]['source_ref']['row'], 4)
        self.assertEqual(result['units'][1]['source_ref']['cells'], ['C4', 'E4'])
        self.assertEqual(result['review_status'], 'unconfirmed')
        self.assertTrue(all(item['review_status'] == 'unconfirmed' for item in result['units']))

    def test_xlsx_formulas_use_only_cached_values(self):
        rows = '<row r="1"><c r="A1" t="str"><f>HYPERLINK("https://example.invalid/")</f><v>3.2.S.7 Stability</v></c><c r="B1"><f>1/0</f></c></row>'
        result = extract_document('cached.xlsx', xlsx_bytes(worksheet(rows)))
        self.assertEqual(result['status'], 'ok')
        self.assertNotIn('HYPERLINK', result['units'][0]['text'])
        self.assertEqual(result['sections'][0]['source_ref']['formula_cells'], ['A1'])
        self.assertEqual(result['sections'][0]['source_ref']['value_mode'], 'stored_values')
        empty = extract_document('uncalculated.xlsx', xlsx_bytes(worksheet('<row r="1"><c r="A1"><f>1+1</f></c></row>')))
        self.assertEqual(empty['status'], 'empty')

    def test_xlsx_corruption_and_unsafe_xml(self):
        self.assertEqual(extract_document('broken.xlsx', b'broken ZIP')['status'], 'error')
        unsafe = '<!DOCTYPE a [<!ENTITY x SYSTEM "file:///etc/passwd">]><a>&x;</a>'
        self.assertEqual(extract_document('unsafe.xlsx', xlsx_bytes(unsafe))['status'], 'error')
        invalid_shared = worksheet('<row r="1"><c r="A1" t="s"><v>9</v></c></row>')
        self.assertEqual(extract_document('bad-index.xlsx', xlsx_bytes(invalid_shared))['status'], 'error')
        invalid_cell = worksheet('<row r="1"><c r="A2"><v>7</v></c></row>')
        self.assertEqual(extract_document('bad-cell.xlsx', xlsx_bytes(invalid_cell))['status'], 'error')
        external = '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="https://example.invalid/sheet.xml" TargetMode="External"/>'
        self.assertEqual(extract_document('external.xlsx', xlsx_bytes(worksheet(''), relationship=external))['status'], 'error')

    def test_xlsx_archive_and_character_bounds(self):
        oversized = xlsx_bytes(worksheet(''), extra={'unused.xml': b' ' * (MAX_XML_BYTES + 1)})
        self.assertEqual(extract_document('archive-limit.xlsx', oversized)['status'], 'limit')
        many_members = xlsx_bytes(worksheet(''), extra={f'unused/{number}.xml': '' for number in range(MAX_ARCHIVE_MEMBERS)})
        self.assertEqual(extract_document('member-limit.xlsx', many_members)['status'], 'limit')
        huge_row = '<row r="1"><c r="A1" t="inlineStr"><is><t>' + 'A' * (MAX_CHARS + 1) + '</t></is></c></row>'
        result = extract_document('text-limit.xlsx', xlsx_bytes(worksheet(huge_row)))
        self.assertTrue(result['truncated'])
        self.assertLessEqual(result['characters'], MAX_CHARS)

    def test_xlsx_cell_scan_bounds(self):
        width = MAX_XLSX_CELLS // 2 + 1
        rows = ''.join(f'<row r="{row}">' + ''.join(f'<c r="{column_name(column)}{row}"/>' for column in range(1, width + 1)) + '</row>' for row in (1, 2))
        result = extract_document('many-cells.xlsx', xlsx_bytes(worksheet(rows)))
        self.assertEqual(result['status'], 'empty')
        self.assertTrue(result['truncated'])

    def test_malformed_and_unsafe_xml(self):
        self.assertEqual(extract_document('broken.pdf', b'%PDF-invalid')['status'], 'error')
        xml = '<!DOCTYPE a [<!ENTITY x SYSTEM "file:///etc/passwd">]><a>&x;</a>'
        self.assertEqual(extract_document('unsafe.docx', docx_bytes(xml))['status'], 'error')

    def test_unsupported_and_bounds(self):
        self.assertEqual(extract_document('ctd.xls', b'not-parsed')['status'], 'unsupported')
        result = extract_document('large.txt', ('A' * (MAX_CHARS + 1)).encode())
        self.assertTrue(result['truncated'])
        self.assertLessEqual(result['characters'], MAX_CHARS)

    def test_no_fabricated_identity(self):
        result = extract_document('no-name.txt', b'Stability study. No identity label here.')
        self.assertEqual(result['drugs'], [])
        self.assertEqual(result['sections'], [])

    def test_ui_session_isolation_and_removal(self):
        root = Path(__file__).resolve().parents[1]
        page = AppTest.from_file(str(root / 'streamlit_app.py'), default_timeout=30)
        page.query_params.update({'enter': '1', 'page': 'documents', 'lang': 'en'})
        page.run()
        self.assertFalse(page.exception)
        state = add_file(new_intake(), 'ctd.txt', SOURCE.encode(), ['CTD.3.2.S.4'])
        page.session_state['customer_document_intake'] = state
        frames = {key: copy.deepcopy(page.session_state[key]) for key in ['evidence_df', 'validation_df', 'profile_values']}
        page.run()
        self.assertFalse(page.exception)
        result = next(iter(page.session_state['customer_document_insights'].values()))
        self.assertEqual(result['drugs'][0]['name'], 'Telmisartan')
        self.assertTrue(any('Telmisartan' in block.value for block in page.code))
        self.assertEqual(page.session_state['customer_document_intake'], state)
        for key, value in frames.items():
            if hasattr(value, 'equals'):
                self.assertTrue(value.equals(page.session_state[key]))
            else:
                self.assertEqual(value, page.session_state[key])
        page.radio(key='language_choice').set_value('ko').run()
        self.assertFalse(page.exception)
        self.assertTrue(any('Telmisartan' in block.value for block in page.code))
        page.session_state['customer_document_intake'] = new_intake()
        page.run()
        self.assertFalse(page.exception)
        self.assertEqual(page.session_state['customer_document_insights'], {})


if __name__ == '__main__':
    unittest.main(verbosity=2)

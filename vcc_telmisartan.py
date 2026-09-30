"""Isolated Telmisartan case review: leaves the existing workbench data intact."""
from __future__ import annotations
import json
import os
import sys
from urllib.parse import urlencode
import pandas as pd
import streamlit as st
from telmisartan_case import load_case, build_handoff, validate_handoff


def _text(ko, en, lang):
    return ko if lang == 'ko' else en


def review_rows(strategy):
    common = [
        ('3.2.S', 'API / DMF', '원료 공급자·제조경로·결정형·불순물 자료와 참조 권한 확인', 'API supplier, process, solid form, impurity evidence and reference rights'),
        ('3.2.P.2', '개발 근거 / Development', strategy['vcc_focus_ko'], strategy['vcc_focus_en']),
        ('3.2.P.5.1 / P.5.6', '규격 / Specification', '함량·유연물질·용출 규격과 설정 근거; 개발 가정을 허용기준으로 단정하지 않기', 'Assay, impurity and dissolution limits with rationale; assumptions are not acceptance criteria'),
        ('3.2.P.5.2 / P.5.3', 'ICH Q14 / Q2(R2)', 'ATP, 성분별 선택성·정확성·범위·정밀성·강건성과 분석법 관리전략 자료', 'ATP, component selectivity, accuracy, range, precision, robustness and method control evidence'),
        ('3.2.P.8', '안정성 / Stability', '가속·장기 안정성, 분해산물, 용출 변화와 포장 적합성', 'Accelerated/long-term stability, degradants, dissolution shifts and packaging suitability'),
        ('3.2.S / P.5', 'ICH Q3D / 불순물', '실제 복용량과 원료·공정 근거로 금속·유전독성·니트로사민 위험 검토 범위 확정', 'Determine elemental, mutagenic and nitrosamine risk scope from actual exposure, materials and process evidence'),
        ('임상·동등성 / Clinical', '허가경로 / Pathway', '한국 대조약·용량·생동/임상 필요 범위, 급여와 특허·실시권 확인', 'Confirm Korean reference, doses, equivalence/clinical scope, reimbursement and IP/licensing'),
        ('NORA', '사업 가정 / Business', '단가·대상환자·접근성·개발비·출시일 근거 확보; 검토결과에 따른 비용·일정 재산정', 'Source price, eligible patients, access, cost and launch timing; revise cost/timing after review'),
    ]
    if strategy['id'] == 'triple':
        common.append(('3.2.P.3 / P.5', '저함량 성분 / Low-dose component', '저함량 성분 균일성·회수율·LOQ와 성분 간 간섭 검토; 미국 승인만으로 한국 경로 확정 불가', 'Low-dose uniformity, recovery, LOQ and interference; US approval does not establish a Korean pathway'))
    return [{'CTD': c, '검토 영역 / Area': a, 'required_ko': ko, 'required_en': en, 'status': '미확인', 'evidence': '', 'action': ''} for c,a,ko,en in common]


def editor_base(key, current):
    # Keep the input frame stable while the widget accumulates edit deltas.
    # When it returns after page/language changes, seed it from durable data.
    base_key = 'tel_vcc_base_' + key
    if key not in st.session_state or base_key not in st.session_state:
        st.session_state[base_key] = current.copy(deep=True)
    return st.session_state[base_key]


def render(lang):
    t = lambda ko,en: _text(ko,en,lang)
    case = load_case()
    strategies = {s['id']: s for s in case['strategies']}
    default = str(st.query_params.get('strategy', 'dual'))
    if default not in strategies:
        default = 'dual'
    st.session_state.setdefault('tel_vcc_strategy', default)
    st.subheader(t('Telmisartan · NORA → VCC 사례 검토', 'Telmisartan · NORA → VCC case review'))
    st.caption(t('한국 개발전략 · 실제 시험 결과와 허가자료는 아직 입력되지 않은 검토용 사례입니다.', 'Korean development strategy · A teaching case without actual test results or a submission dossier.'))
    with st.expander(t('NORA에서 수정한 가정 불러오기', 'Import assumptions edited in NORA')):
        uploaded = st.file_uploader(t('NORA 전달 JSON', 'NORA handoff JSON'), type=['json'], key='tel_vcc_upload')
        if st.button(t('패킷 검증 후 적용', 'Validate and apply packet'), key='tel_vcc_apply', disabled=uploaded is None):
            try:
                if uploaded.size > 100_000:
                    raise ValueError('패킷은 100 KB 이하여야 합니다.')
                packet = validate_handoff(json.loads(uploaded.getvalue().decode('utf-8')))
                st.session_state['tel_vcc_packet_'+packet['strategy_id']] = packet
                st.session_state.tel_vcc_strategy = packet['strategy_id']
                st.success(t('가정을 불러오고 매출을 다시 계산했습니다.', 'Assumptions imported; revenue recalculated.'))
            except (ValueError, TypeError, UnicodeError) as exc:
                st.error(str(exc))
    selected = st.selectbox(t('개발전략', 'Development strategy'), list(strategies),
                            format_func=lambda key: strategies[key]['label_'+lang], key='tel_vcc_strategy')
    strategy = strategies[selected]
    imported = st.session_state.get('tel_vcc_packet_'+selected)
    packet = imported or build_handoff(selected, strategy['assumptions'])
    st.info(t('NORA 파일에서 불러온 가정' if imported else '기본 가정 사례 · NORA에서 변경한 값은 JSON을 내려받아 위에서 불러오세요.',
              'Imported NORA assumptions' if imported else 'Default teaching assumptions · To transfer edited values, download the NORA JSON and import it above.'))
    st.write('**'+strategy['composition_'+lang]+'**')
    st.write(strategy['development_'+lang])
    summary = packet['summary']
    c1,c2,c3 = st.columns(3)
    c1.metric(t('출시 가정', 'Assumed launch'), str(summary['launch_year']))
    c2.metric(t('기간 내 위험조정 최대 매출', 'Risk-adjusted peak in horizon'), f"{summary['peak_risk_adjusted_krw_m']/100:,.1f} "+t('억원','KRW 100M'))
    c3.metric(t('개발비 가정', 'Assumed development cost'), f"{summary['development_cost_krw_m']/100:,.1f} "+t('억원','KRW 100M'))
    st.caption(t('2027–2034년 가정 계산입니다. VCC 점검 상태를 성공확률로 자동 변환하지 않습니다.', 'Hypothetical 2027–2034 calculation. VCC review status is not converted into probability of success.'))
    docs, calculations, handoff = st.tabs([t('개발·문서 검토', 'Development and documents'), t('농도·밸리데이션', 'Concentration and validation'), t('NORA 연계·내보내기', 'NORA link and export')])
    with docs:
        state_key = 'tel_vcc_reviews_'+selected
        st.session_state.setdefault(state_key, pd.DataFrame(review_rows(strategy)))
        df = st.session_state[state_key].copy()
        required = 'required_'+lang
        view = df[['CTD','검토 영역 / Area',required,'status','evidence','action']].copy()
        editor_key = 'tel_vcc_review_editor_'+selected+'_'+lang
        edited = st.data_editor(editor_base(editor_key, view), hide_index=True, width='stretch', key=editor_key,
             disabled=['CTD','검토 영역 / Area',required], column_config={
                 required:st.column_config.TextColumn(t('확보할 근거','Evidence needed'),width='large'),
                 'status':st.column_config.SelectboxColumn(t('검토 상태','Review status'),options=['미확인','확인','보완 필요','해당 없음'],required=True),
                 'evidence':st.column_config.TextColumn(t('문서·원문 근거','Document/source evidence')),
                 'action':st.column_config.TextColumn(t('다음 조치·담당','Next action / owner'))})
        for col in ['status','evidence','action']:
            df[col] = edited[col]
        st.session_state[state_key] = df
        unresolved = int(df['status'].isin(['미확인','보완 필요']).sum())
        st.write(t(f'확인할 항목 {unresolved}개. 일정·개발비에 미치는 영향을 NORA 가정에 반영하세요.', f'{unresolved} open items. Reflect timing and development-cost impacts in NORA assumptions.'))
        st.caption(t('검토 항목은 사례에 맞춘 분석 제안입니다. 확정된 허가 요구사항이나 실험 결과가 아닙니다.', 'These are proposed case-review questions, not confirmed regulatory requirements or experimental results.'))
    with calculations:
        app = sys.modules['app']
        st.write(t('기존 VCC 계산식으로 성분별 농도를 확인합니다.', 'Check component concentrations using the existing VCC calculation.'))
        st.caption(t('교육용 조제·허용기준 가정입니다. 투여량 또는 확정된 시험법을 제안하지 않습니다. 실제 시험 결과는 비워 두었습니다.', 'Teaching preparation and limit assumptions; not a dosing or validated-method recommendation. Actual results are blank.'))
        names = ['Telmisartan'] + (['Amlodipine'] if selected != 'generic' else []) + (['Indapamide'] if selected == 'triple' else [])
        amounts = dict(Telmisartan=40.0,Amlodipine=5.0,Indapamide=2.5)
        prep_key='tel_vcc_prep_'+selected
        if prep_key not in st.session_state:
            st.session_state[prep_key]=pd.DataFrame([{'Component':n,'Reference ug/mL':amounts[n],'Weighed mg':amounts[n],'Purity %':100.0,'Stock mL':100.0,'Aliquot mL':5.0,'Final mL':50.0,'Dilution':1.0} for n in names])
        prep_editor_key = 'tel_vcc_prep_editor_'+selected
        prep = st.data_editor(editor_base(prep_editor_key, st.session_state[prep_key]),key=prep_editor_key,hide_index=True,width='stretch',disabled=['Component'],
            column_config={c:st.column_config.NumberColumn(c,min_value=.000001) for c in ['Reference ug/mL','Weighed mg','Purity %','Stock mL','Aliquot mL','Final mL','Dilution']})
        st.session_state[prep_key]=prep
        results=[]
        for _,row in prep.iterrows():
            numeric=[row[c] for c in prep.columns if c!='Component']
            if any(pd.isna(v) or not 0<float(v)<float('inf') for v in numeric) or row['Purity %']>100:
                st.error(t('양수 입력값과 100% 이하 순도를 확인하세요.', 'Check positive inputs and purity at or below 100%.'))
                continue
            result=app.calculate_sample_prep(row['Reference ug/mL'],100,row['Weighed mg'],row['Purity %'],row['Stock mL'],row['Aliquot mL'],row['Final mL'],row['Dilution'])
            results.append({'Component':row['Component'],'Actual ug/mL':result['final_conc'],'Target ug/mL':result['target_conc'],'Difference %':result['diff_pct'],'Preparation check':result['gate']})
        st.dataframe(pd.DataFrame(results),hide_index=True,width='stretch')
        st.caption(t('조제 차이의 Pass/Review/Hold는 기존 내부 계산 규칙입니다. 분석법 밸리데이션 통과를 의미하지 않습니다.', 'Preparation Pass/Review/Hold uses existing internal calculation rules; it is not validation approval.'))
        rule_key='tel_vcc_rules_'+selected
        st.session_state.setdefault(rule_key,pd.DataFrame([{'Component':n,'Check':'Assay recovery (illustrative)','Result':float('nan'),'Rule':'between','Lower':98.0,'Upper':102.0,'Unit':'%'} for n in names]))
        rule_editor_key = 'tel_vcc_rule_editor_'+selected
        rules=st.data_editor(editor_base(rule_editor_key, st.session_state[rule_key]),key=rule_editor_key,hide_index=True,width='stretch',disabled=['Component','Check','Unit'],column_config={'Rule':st.column_config.SelectboxColumn('Rule',options=['between','gte','lte','info'],required=True)})
        st.session_state[rule_key]=rules
        output=rules.copy();output['Review state']=output.apply(app.evaluate_rule,axis=1)
        st.dataframe(output,hide_index=True,width='stretch')
        st.caption(t('결과 미입력은 Info입니다. 각 성분·시험법의 근거에 따라 규칙과 허용기준을 조정하세요.', 'Blank results are Info. Adjust rules and limits using evidence for each component and method.'))
    with handoff:
        nora_url=os.environ.get('NORA_APP_URL','https://toxiguard-rf.streamlit.app/').rstrip('/')+'/?'+urlencode({'case':'telmisartan'})
        st.link_button(t('NORA 전략 비교 열기','Open NORA strategy comparison'),nora_url)
        st.write(t('문서·시험 검토에서 확인한 지연·추가시험·개발비를 NORA 가정에 직접 반영하고 다시 비교하세요.', 'Update NORA timing and cost assumptions from documentary gaps, additional studies and development work, then compare again.'))
        st.json(packet['assumptions'],expanded=False)
        memo = '# Telmisartan · NORA / VCC\n\n' + strategy['label_'+lang]+'\n\n'+strategy['composition_'+lang]+'\n\n'
        memo += t('가정 기반 사례. 실제 시험결과·허가판정 아님.\n\n','Hypothetical case. Not actual test results or regulatory approval.\n\n')
        memo += json.dumps(packet,ensure_ascii=False,indent=2)+'\n\n## Document review\n\n'+df.to_csv(index=False)
        memo += '\n## Preparation calculations\n\n'+pd.DataFrame(results).to_csv(index=False)+'\n## Editable validation checks\n\n'+output.to_csv(index=False)
        memo += '\n## Sources\n\n'+'\n'.join(f"- {s['title']}: {s['url']}" for s in case['sources'])
        st.download_button(t('사례 검토 메모 다운로드','Download case-review memo'),memo.encode('utf-8'),file_name='telmisartan-vcc-review.md',mime='text/markdown',key='tel_vcc_memo')
        st.download_button(t('적용한 NORA 가정 다운로드','Download applied NORA assumptions'),json.dumps(packet,ensure_ascii=False,indent=2).encode('utf-8'),file_name='telmisartan-nora-handoff.json',mime='application/json',key='tel_vcc_packet_download')
    with st.expander(t('공개 근거·자료 범위','Public evidence and scope')):
        for source in case['sources']:
            st.markdown(f"- [{source['title']}]({source['url']}) · {source.get('date','')}\n  {source.get('note','')}")

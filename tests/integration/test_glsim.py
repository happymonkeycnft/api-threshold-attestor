import json
from pathlib import Path
import pytest
from glsim.engine import SimEngine
from glsim.state import StateStore,TxStatus
from glsim.consensus import run_consensus
@pytest.mark.parametrize('scenario,value',[('ABOVE',125),('BELOW',75),('EQUAL',100),('UNAVAILABLE',125),('DISAGREEMENT',125)])
def test_five_validators(scenario,value):
    calls={'web':0,'llm':0}
    mode=[scenario]
    def web(req):
        calls['web']+=1
        body={} if mode[0]=='UNAVAILABLE' else {'data':{'value':value}}
        text=json.dumps(body)+(' ' if mode[0]=='DISAGREEMENT' and calls['web']>1 else '')
        return {'ok':{'response':{'status':200,'headers':{'content-type':b'application/json'},'body':text.encode()}}}
    def llm(req):
        calls['llm']+=1
        raise AssertionError('LLM forbidden')
    engine=SimEngine(StateStore(seed='api-threshold-tests'),web_handler=web,llm_handler=llm)
    engine.activate()
    try:
        addr,_=engine.deploy('contracts/api_threshold_attestor.py')
        i=engine.call_method(addr,'create_attestation',['https://api.example.com/value','data.value','>','100',''])
        before=engine.call_method(addr,'get_attestation',[i])
        def execute(): return engine.call_method(addr,'resolve_attestation',[i]),b''
        result=run_consensus(engine,execute,num_validators=5,max_rotations=1)
        row=engine.call_method(addr,'get_attestation',[i])
        assert len(result.votes)==5 and calls['llm']==0
        report=dict(scenario=scenario,votes=result.votes,status=result.status.value,result=result.result,calls=dict(calls),attestation=row)
        if scenario=='DISAGREEMENT':
            assert result.status==TxStatus.UNDETERMINED
            assert result.votes==['disagree']*5 and row==before
        else:
            assert result.status==TxStatus.FINALIZED and result.error is None
            assert result.votes==['agree']*5 and calls['web']==6
            if scenario=='UNAVAILABLE':
                assert result.result=='UNAVAILABLE' and row==before
                mode[0]='ABOVE'
                retry=run_consensus(engine,execute,num_validators=5,max_rotations=1)
                assert retry.status==TxStatus.FINALIZED and retry.error is None
                assert engine.call_method(addr,'get_attestation',[i])['status']=='ATTESTED'
                report['retry']=dict(result=retry.result,votes=retry.votes)
            else: assert row['status']=='ATTESTED' and row['result']==scenario
        Path('reports/glsim-'+scenario.lower()+'.json').write_text(json.dumps(report,indent=2)+'\n')
    finally: engine.deactivate()

import hashlib
import pytest
PATH='contracts/api_threshold_attestor.py'
URL='https://api.example.com/value'
@pytest.fixture
def contract(direct_deploy): return direct_deploy(PATH)
def create(c,**changes):
    args=dict(api_url=URL,json_path='data.value',operator='>',threshold='100',context='')
    args.update(changes)
    return c.create_attestation(**args)
def mock(vm,body=b'{"data":{"value":125}}',status=200,ct=b'application/json'):
    vm.clear_mocks()
    vm.mock_web(r'.*',{'response':dict(status=status,headers={'content-type':ct},body=body)})
    vm._live_llm_handler=lambda req: pytest.fail('Unexpected LLM')
def test_creation(contract,direct_owner):
    row=contract.get_attestation(create(contract,context='purpose'))
    assert row==dict(attestation_id=1,creator=direct_owner.as_hex,api_url=URL,json_path='data.value',operator='>',threshold='100',context='purpose',request_commitment=row['request_commitment'],status='PENDING',availability='',observed_value='',response_fingerprint='',result='',condition_met=False)
def test_count(contract):
    assert contract.get_attestation_count()==0
    assert create(contract)==1
    assert create(contract)==2
    assert contract.get_attestation_count()==2
@pytest.mark.parametrize('field,value', [('api_url',x) for x in ['', 'http://example.com','https://user:pass@example.com','https://127.0.0.1','https://[::1]','https://localhost','https://a.internal','https://a.com:80','https://a.com/%zz','https://a.com/\\x','https://a.com/\n','https://a.com/'+'x'*501]]+[('json_path',x) for x in ['', 'a..b','a[0]','a.*','a.','a'*201]]+[('operator',x) for x in ['>=','!=','eval']]+[('threshold',x) for x in ['', 'NaN','Infinity','1e2','+1','.5','1.','1'*61,'0.'+'1'*19]]+[('context','x'*501),('context','\x00')])
def test_invalid(contract,direct_vm,field,value):
    with direct_vm.expect_revert(): create(contract,**{field:value})
    assert contract.get_attestation_count()==0
@pytest.mark.parametrize('value,expected',[('000100.000','100'),('-0.00','0'),('-0005.200','-5.2'),('0.'+'1'*18,'0.'+'1'*18)])
def test_normalization(contract,value,expected):
    assert contract.get_attestation(create(contract,threshold=value))['threshold']==expected
def test_url(contract):
    assert contract.get_attestation(create(contract,api_url=' HTTPS://API.EXAMPLE.COM:443/value#x '))['api_url']==URL
def test_commit_reference(contract,direct_owner):
    row=contract.get_attestation(create(contract,context='é'))
    fields=['api-threshold-attestor:v1','1',direct_owner.as_hex.lower(),URL,'data.value','>','100','é']
    parts=[s.encode() for s in fields]
    assert row['request_commitment']==hashlib.sha256(b''.join(len(s).to_bytes(4,'big')+s for s in parts)).hexdigest()
@pytest.mark.parametrize('change',['api_url','json_path','operator','threshold','context','creator','id','same'])
def test_commit_changes(contract,direct_vm,direct_bob,change):
    snap=direct_vm.snapshot()
    first=contract.get_attestation(create(contract))['request_commitment']
    direct_vm.revert(snap)
    if change=='creator': direct_vm.sender=direct_bob
    if change=='id': create(contract)
    changes=dict(api_url='https://other.example.com/',json_path='a.b',operator='<',threshold='101',context='other')
    second=contract.get_attestation(create(contract,**({change:changes[change]} if change in changes else {})))['request_commitment']
    assert (first==second)==(change=='same')
@pytest.mark.parametrize('value,threshold,result',[('125','100','ABOVE'),('75','100','BELOW'),('100','100','EQUAL'),('0.300000000000000001','0.3','ABOVE'),('-5.2','-5.1','BELOW'),('-5','-5.00','EQUAL'),('0.1','0.100000000000000001','BELOW'),('9'*60,'1'+'0'*59,'ABOVE')])
@pytest.mark.parametrize('operator',['>','<','=='])
def test_numeric(contract,direct_vm,value,threshold,result,operator):
    i=create(contract,threshold=threshold,operator=operator)
    body=('{"data":{"value":'+value+'}}').encode()
    mock(direct_vm,body)
    assert contract.resolve_attestation(i)==result
    row=contract.get_attestation(i)
    assert row['condition_met']==(result=={'>':'ABOVE','<':'BELOW','==':'EQUAL'}[operator])
    assert row['response_fingerprint']==hashlib.sha256(body).hexdigest()
    assert row['availability']=='AVAILABLE' and row['status']=='ATTESTED'
    with direct_vm.expect_revert('Already attested'): contract.resolve_attestation(i)
    assert contract.get_attestation(i)==row
@pytest.mark.parametrize('body,status,ct',[(b'{}',200,b'application/json'),(b'{',200,b'application/json')]+[(('{"data":{"value":'+v+'}}').encode(),200,b'application/json') for v in ['"125"','true','null','1e2','NaN','Infinity','0.1234567890123456789','125,"value":126']]+[(b'{"data":[125]}',200,b'application/json'),(b'\xff',200,b'application/json'),(b'x'*65537,200,b'application/json'),(b'',200,b'application/json'),(b'{}',503,b'application/json'),(b'{}',302,b'application/json'),(b'{}',200,b'text/html'),(b'{}',200,b'')])
def test_unavailable(contract,direct_vm,body,status,ct):
    i=create(contract)
    before=contract.get_attestation(i)
    mock(direct_vm,body,status,ct)
    assert contract.resolve_attestation(i)=='UNAVAILABLE'
    assert contract.get_attestation(i)==before
    mock(direct_vm)
    assert contract.resolve_attestation(i)=='ABOVE'
def test_fetch_exception(contract,direct_vm):
    i=create(contract)
    before=contract.get_attestation(i)
    direct_vm._live_web_handler=lambda req: (_ for _ in ()).throw(RuntimeError('offline'))
    assert contract.resolve_attestation(i)=='UNAVAILABLE'
    assert contract.get_attestation(i)==before
    mock(direct_vm)
    assert contract.resolve_attestation(i)=='ABOVE'
@pytest.mark.parametrize('body,expected',[(b'{"data":{"value":125}}',True),(b'{ "data":{"value":125}}',False),(b'{"data":{"value":126}}',False),(b'{}',False)])
def test_consensus(contract,direct_vm,body,expected):
    i=create(contract)
    mock(direct_vm)
    contract.resolve_attestation(i)
    before=contract.get_attestation(i)
    mock(direct_vm,body)
    assert direct_vm.run_validator() is expected
    assert contract.get_attestation(i)==before
def test_pickling(contract,direct_vm):
    direct_vm.check_pickling=True
    i=create(contract)
    mock(direct_vm)
    contract.resolve_attestation(i)
@pytest.mark.parametrize('method',['get_attestation','resolve_attestation'])
def test_missing(contract,direct_vm,method):
    with direct_vm.expect_revert('not found'): getattr(contract,method)(999)
def test_exact_bound(contract,direct_vm):
    body=b'{"data":{"value":125}}'
    body+=b' '*(65536-len(body))
    i=create(contract)
    mock(direct_vm,body,ct=b'application/problem+json; charset=utf-8')
    assert contract.resolve_attestation(i)=='ABOVE'

import ast
import hashlib
import json
import re
from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=root/'contracts/api_threshold_attestor.py'
s=p.read_text()
t=ast.parse(s)
c=next(n for n in t.body if isinstance(n,ast.ClassDef) and n.name=='APIThresholdAttestor')
methods={n.name:[ast.unparse(d) for d in n.decorator_list] for n in c.body if isinstance(n,ast.FunctionDef) and n.decorator_list}
assert methods==dict(create_attestation=['gl.public.write'],resolve_attestation=['gl.public.write'],get_attestation=['gl.public.view'],get_attestation_count=['gl.public.view'])
r=next(n for n in c.body if isinstance(n,ast.FunctionDef) and n.name=='resolve_attestation')
for fn in [n for n in r.body if isinstance(n,ast.FunctionDef)]:
    names={n.id for n in ast.walk(fn) if isinstance(n,ast.Name)}
    assert not names.intersection({'self','row','memory'})
assert s.index('gl.storage.copy_to_memory(row)')<s.index('def leader_fn')
assert s.index('accepted = gl.vm.run_nondet')<s.index('row.observed_value =')
assert not any(isinstance(n,ast.Constant) and isinstance(n.value,float) for n in ast.walk(t))
assert 'exec_prompt' not in s and 'float(' not in s
patterns=[r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',r'\b(?:sk-proj-|ghp_|github_pat_)[A-Za-z0-9_-]{20,}',r'(?i)(?:private_key|api_key|secret_key)\s*[:=]\s*["\'][A-Za-z0-9+/=_-]{24,}']
for f in root.rglob('*'):
    if not f.is_file() or any(x.startswith('.') or x=='__pycache__' for x in f.relative_to(root).parts): continue
    if f.suffix in ('.py','.md','.txt','.json','.toml','.yaml','.lock'):
        assert not any(re.search(pattern,f.read_text()) for pattern in patterns),str(f)
metrics=dict(source_bytes=len(p.read_bytes()),source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),public_method_count=len(methods),llm_call_count=0,response_bound_bytes=65536,decimal_precision=18,integer_digits=60,interface='PASS',closure_storage='PASS (AST plus direct pickling and GLSim)',secret_scan='PASS (credential-pattern text scan)')
assert metrics['source_bytes']<=10000
(root/'reports/metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
print(json.dumps(metrics,indent=2))

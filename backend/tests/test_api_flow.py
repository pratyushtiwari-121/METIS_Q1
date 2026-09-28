import sys
sys.path.insert(0, 'backend')
from fastapi.testclient import TestClient
from app.main import app

def test_full_qds():
    c = TestClient(app)
    kg = c.post('/api/qds/keygen', json={'length': 8, 'seed': 42}).json()
    assert 'key_id' in kg, kg
    key_id = kg['key_id']
    print('Keygen OK:', key_id)

    dist = c.post('/api/qds/distribute', json={'key_id': key_id, 'verifiers': ['Bob', 'Charlie'], 'seed': 42}).json()
    assert 'total_states_teleported' in dist, dist
    print('Distribute OK, total teleported:', dist['total_states_teleported'])

    sign = c.post('/api/qds/sign', json={'key_id': key_id, 'message': 'Authorize transaction #42', 'bit': 1}).json()
    assert 'signature_id' in sign, sign
    print('Sign OK, signature_id:', sign['signature_id'])

    verify = c.post('/api/qds/verify', json={
        'key_id': key_id,
        'signature_id': sign['signature_id'],
        'message': 'Authorize transaction #42',
        'bit': 1,
        'verifier_id': 'Bob',
        'seed': 42
    }).json()
    assert 'decision' in verify, verify
    print('Verify decision:', verify['decision'], 'mismatch_rate:', verify['mismatch_rate'])

    mem = c.get(f'/api/qds/memory/{key_id}/Bob')
    assert mem.status_code == 200, mem.text
    print('Memory GET status:', mem.status_code)

if __name__ == '__main__':
    test_full_qds()

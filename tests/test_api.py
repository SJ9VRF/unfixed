from fastapi.testclient import TestClient
from api.app import app

def test_api_health_and_simulate():
    c=TestClient(app)
    assert c.get('/health').json()['status']=='ok'
    r=c.post('/simulate',json={'user_id':'x','seed':1,'interactions':3})
    assert r.status_code==200
    assert len(r.json()['events'])==3

def test_demo_route_served():
    from fastapi.testclient import TestClient
    from api.app import app
    r=TestClient(app).get('/demo')
    assert r.status_code==200
    assert 'The Unfixed User' in r.text

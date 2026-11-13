from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app)
def test_health():
 r=client.get('/api/health');assert r.status_code==200;assert r.json()['model_ready'] is False
def test_invalid_upload():assert client.post('/api/predict',files={'file':('bad.jpg',b'bad','image/jpeg')}).status_code==422
def test_unknown_record():assert client.get('/api/knowledge/not-a-plant').status_code==404

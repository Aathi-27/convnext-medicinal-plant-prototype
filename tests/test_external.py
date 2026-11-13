import io,json,sqlite3
import pytest
from PIL import Image
from app import external

def photo():
 b=io.BytesIO();Image.new('RGB',(90,70),'green').save(b,format='JPEG',exif=Image.Exif());return b.getvalue()

def test_photo_cleaning():
 clean=external.prepare_photo(photo())
 im=Image.open(io.BytesIO(clean));assert im.size==(90,70);assert not im.getexif()

@pytest.mark.parametrize('raw',[b'',b'bad',b'a'*(10*1024*1024+1)])
def test_bad_photo(raw):
 with pytest.raises(external.InputError):external.prepare_photo(raw)

def test_small_photo():
 b=io.BytesIO();Image.new('RGB',(10,10)).save(b,format='PNG')
 with pytest.raises(external.InputError):external.prepare_photo(b.getvalue())

def test_parser():
 d={'scientific_name':'Curcuma longa','common_name':'Turmeric','confidence_label':'low','uncertainty':'Leaves insufficient','visible_features':['green leaves']}
 r=external.parse_suggestion(json.dumps(d));assert r['provenance']=='external_ai';assert r['status']=='unverified';assert 'score' not in r['suggestion']
 for bad in ['not json','[]',json.dumps({**d,'confidence_label':'99%'}),json.dumps({**d,'scientific_name':['x']}),json.dumps({**d,'visible_features':['a']*9})]:
  with pytest.raises(external.ExternalError):external.parse_suggestion(bad)

def test_minute_and_daily_caps(tmp_path,monkeypatch):
 p=tmp_path/'limits.sqlite';monkeypatch.setenv('FALLBACK_STATE_DB',str(p))
 for _ in range(3):external.reserve_call()
 with pytest.raises(external.ExternalError) as e:external.reserve_call()
 assert e.value.status==429
 with sqlite3.connect(p) as db:db.execute('UPDATE calls SET ts=ts-61');db.executemany('INSERT INTO calls VALUES (?)',[(external.time.time()-100,)]*57)
 with pytest.raises(external.ExternalError) as e:external.reserve_call()
 assert e.value.status==429

def test_no_consent_no_transfer(monkeypatch):
 from fastapi.testclient import TestClient
 from app.main import app
 def fail(*a):raise AssertionError('must not transfer')
 monkeypatch.setattr(external,'identify',fail)
 r=TestClient(app).post('/api/external-suggestion',files={'file':('leaf.jpg',photo(),'image/jpeg')})
 assert r.status_code==400

def test_api_validation_and_mock(monkeypatch):
 from fastapi.testclient import TestClient
 from app.main import app
 monkeypatch.setenv('EXTERNAL_FALLBACK_ENABLED','1');monkeypatch.setenv('GROQ_API_KEY_FILE','/not-read-in-mock')
 monkeypatch.setattr(external,'identify',lambda p:{'status':'unverified','provenance':'external_ai'})
 c=TestClient(app)
 assert c.post('/api/external-suggestion',data={'consent':'true'},files={'file':('leaf.jpg',photo(),'image/jpeg')}).json()['status']=='unverified'
 assert c.post('/api/external-suggestion',data={'consent':'true'},files={'file':('bad.jpg',b'bad','image/jpeg')}).status_code==422
 assert c.post('/api/external-suggestion',headers={'sec-fetch-site':'cross-site'},data={'consent':'true'},files={'file':('leaf.jpg',photo(),'image/jpeg')}).status_code==403

def test_fail_closed_missing_key(monkeypatch):
 monkeypatch.setenv('EXTERNAL_FALLBACK_ENABLED','1');monkeypatch.setenv('GROQ_API_KEY_FILE','/nonexistent-key')
 with pytest.raises(external.ExternalError) as e:external.identify(b'photo')
 assert e.value.status==503

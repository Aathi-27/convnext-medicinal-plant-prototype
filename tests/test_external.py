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
 d={'explanation':'Trifoliate leaves consistent with Bael.','supporting_features':['three leaflets'],'closest_alternatives':['Brahmi']}
 r=external.parse_explanation(json.dumps(d),'Bael','Aegle marmelos');assert r['provenance']=='external_ai';assert r['status']=='unverified';assert r['explanation']['predicted_common_name']=='Bael'
 for bad in ['not json','[]',json.dumps({**d,'explanation':['x']}),json.dumps({**d,'supporting_features':['a']*9}),json.dumps({**d,'closest_alternatives':['a']*5})]:
  with pytest.raises(external.ExternalError):external.parse_explanation(bad,'Bael','Aegle marmelos')

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
 monkeypatch.setattr(external,'explain',fail)
 r=TestClient(app).post('/api/external-suggestion',files={'file':('leaf.jpg',photo(),'image/jpeg')})
 assert r.status_code==400

def test_api_validation_and_mock(monkeypatch):
 from fastapi.testclient import TestClient
 from app.main import app
 monkeypatch.setenv('EXTERNAL_FALLBACK_ENABLED','1');monkeypatch.setenv('GROQ_API_KEY_FILE','/not-read-in-mock')
 monkeypatch.setattr(external,'explain',lambda p,c,s2:{'status':'unverified','provenance':'external_ai'})
 c=TestClient(app)
 assert c.post('/api/external-suggestion',data={'consent':'true','predicted_common':'Bael','predicted_scientific':'Aegle marmelos'},files={'file':('leaf.jpg',photo(),'image/jpeg')}).json()['status']=='unverified'
 assert c.post('/api/external-suggestion',data={'consent':'true'},files={'file':('bad.jpg',b'bad','image/jpeg')}).status_code==422
 assert c.post('/api/external-suggestion',headers={'sec-fetch-site':'cross-site'},data={'consent':'true'},files={'file':('leaf.jpg',photo(),'image/jpeg')}).status_code==403

def test_fail_closed_missing_key(monkeypatch):
 monkeypatch.setenv('EXTERNAL_FALLBACK_ENABLED','1');monkeypatch.setenv('GROQ_API_KEY_FILE','/nonexistent-key')
 with pytest.raises(external.ExternalError) as e:external.explain(b'photo','Bael','Aegle marmelos')
 assert e.value.status==503
 with pytest.raises(external.ExternalError) as e:external.explain(b'photo','','')
 assert e.value.status==400

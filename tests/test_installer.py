import hashlib,io
import pytest
from scripts.install_model import download

def test_https_required(tmp_path):
 with pytest.raises(ValueError,match='HTTPS'):download('http://example.com/x',tmp_path/'x','0'*64)

def test_changed_bytes_not_installed(tmp_path,monkeypatch):
 class Response(io.BytesIO):url='https://example.com/model'
 monkeypatch.setattr('urllib.request.urlopen',lambda *a,**k:Response(b'bad'))
 with pytest.raises(ValueError,match='checksum'):download('https://example.com/model',tmp_path/'x','0'*64)
 assert list(tmp_path.iterdir())==[]

def test_good_bytes_installed_atomically(tmp_path,monkeypatch):
 class Response(io.BytesIO):url='https://example.com/model'
 monkeypatch.setattr('urllib.request.urlopen',lambda *a,**k:Response(b'good'))
 download('https://example.com/model',tmp_path/'x',hashlib.sha256(b'good').hexdigest())
 assert (tmp_path/'x').read_bytes()==b'good'

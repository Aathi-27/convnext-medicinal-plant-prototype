"""Download the small CC BY-SA4.0 internal pilot. Not a validated dataset."""
import json,hashlib,time,urllib.request
from pathlib import Path
root=Path(__file__).resolve().parents[1]
for row in json.loads((root/'data/pilot-manifest.json').read_text()):
    path=root/row['path'];path.parent.mkdir(parents=True,exist_ok=True)
    if not path.exists():
        path.write_bytes(urllib.request.urlopen(row['m'],timeout=30).read());time.sleep(.5)
    assert hashlib.sha256(path.read_bytes()).hexdigest()==row['sha256'], 'Source bytes changed; review before use'
print('Pilot images checked. Retain author/source/license fields; do not treat community labels as expert verification.')

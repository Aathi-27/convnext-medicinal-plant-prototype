"""Build only the exact attributed experimental snapshot. No rejected candidates."""
import json,urllib.request,hashlib,zipfile,csv,io,time,concurrent.futures
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
rows=json.loads((ROOT/'data/dataset-v0.3/manifest.json').read_text());out=ROOT/'dataset-release';out.mkdir(exist_ok=True)
def fetch(r):
 p=out/r['path'];p.parent.mkdir(parents=True,exist_ok=True)
 if not p.exists():
  assert r['m'].startswith(('https://bs.plantnet.org/','https://inaturalist-open-data.s3.amazonaws.com/','https://static.inaturalist.org/')),'Unexpected source host'
  with urllib.request.urlopen(r['m'],timeout=30) as response:b=response.read(10*1024*1024+1)
  assert len(b)<=10*1024*1024 and hashlib.sha256(b).hexdigest()==r['sha256'],'Changed source bytes; review before release';p.write_bytes(b)
 assert hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256'];time.sleep(.3)
 return p
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:list(ex.map(fetch,rows))
assets=ROOT/'release-assets';assets.mkdir(exist_ok=True)
for i,ids in enumerate([['ashwagandha','bael','brahmi','catnip'],['lemon_balm','neem','peppermint'],['stevia','tulsi','turmeric']],1):
 p=assets/f'medicinal-plant-dataset-v0.3-part{i}.zip'
 with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED) as z:
  for r in rows:
   if r['species_id'] in ids:z.write(out/r['path'],r['path'])
  for f in (ROOT/'data/dataset-v0.3').iterdir():
   if f.is_file():z.write(f,f.name)
 print(p.name,p.stat().st_size,flush=True)
(assets/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n' for p in sorted(assets.glob('*.zip'))))

"""Install an explicitly supplied, checksum-pinned artifact. No default remote model."""
import argparse,hashlib,json,os,tempfile,urllib.request,urllib.parse
from pathlib import Path

def download(url,target,expected,max_bytes=150*1024*1024):
 if urllib.parse.urlparse(url).scheme!='https':raise ValueError('Model source must use HTTPS')
 target=Path(target);target.parent.mkdir(parents=True,exist_ok=True)
 if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest()==expected:return
 temp=None
 try:
  with urllib.request.urlopen(url,timeout=120) as response:
   if urllib.parse.urlparse(response.url).scheme!='https':raise ValueError('Redirect left HTTPS')
   with tempfile.NamedTemporaryFile(dir=target.parent,delete=False) as f:
    temp=Path(f.name);h=hashlib.sha256();n=0
    while True:
     b=response.read(1024*1024)
     if not b:break
     n+=len(b)
     if n>max_bytes:raise ValueError('Artifact exceeds size limit')
     h.update(b);f.write(b)
  if h.hexdigest()!=expected:raise ValueError('Artifact checksum mismatch')
  os.replace(temp,target);temp=None
 finally:
  if temp is not None:temp.unlink(missing_ok=True)

def main():
 p=argparse.ArgumentParser();p.add_argument('--metadata',required=True);p.add_argument('--url',required=True);p.add_argument('--output',required=True);a=p.parse_args();meta=json.loads(Path(a.metadata).read_text())
 if meta.get('architecture')!='convnext_tiny' or not meta.get('trained'):raise ValueError('Unsupported model metadata')
 name=meta['file']
 if Path(name).name!=name:raise ValueError('Model filename must be a basename')
 out=Path(a.output);download(a.url,out/name,meta['sha256']);(out/'model.json').write_text(json.dumps(meta,indent=2))
if __name__=='__main__':main()

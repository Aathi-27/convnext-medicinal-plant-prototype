"""Development-only linear-head comparison. Excludes every read test/audit photo."""
import json,hashlib,copy,argparse,time
from pathlib import Path
import torch
from torch import nn
from torchvision.models import convnext_tiny,ConvNeXt_Tiny_Weights
from torchvision import transforms as T
from torchvision.transforms import InterpolationMode
from PIL import Image,ImageOps
p=argparse.ArgumentParser();p.add_argument('--manifest',required=True);p.add_argument('--out',required=True);a=p.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=True);rows=[z for z in json.load(open(a.manifest)) if z['split'] in ['train','val','mint_dev_val']];ids=[z['id'] for z in json.load(open(Path(__file__).resolve().parents[1]/'data/species.json'))];torch.set_num_threads(2);torch.manual_seed(42);m=convnext_tiny(weights=ConvNeXt_Tiny_Weights.IMAGENET1K_V1);m.classifier[2]=nn.Identity();m.eval();prep=T.Compose([T.Resize((224,224),interpolation=InterpolationMode.BICUBIC),T.ToTensor(),T.Normalize([.485,.456,.406],[.229,.224,.225])]);features=[]
with torch.inference_mode():
 for start in range(0,len(rows),4):
  batch=[]
  for z in rows[start:start+4]:
   assert hashlib.sha256(Path(z['path']).read_bytes()).hexdigest()==z['sha256']
   with Image.open(z['path']) as im:batch.append(prep(ImageOps.exif_transpose(im).convert('RGB')))
  features.append(m(torch.stack(batch)).clone())
x=torch.cat(features).clone();y=torch.tensor([ids.index(z['species_id']) for z in rows]);indices={s:torch.tensor([i for i,z in enumerate(rows) if z['split']==s]) for s in ['train','val','mint_dev_val']};head=nn.Linear(768,10);opt=torch.optim.AdamW(head.parameters(),lr=.01,weight_decay=.01);lossfn=nn.CrossEntropyLoss();best=float('inf');state=None;stale=0;history=[]
for epoch in range(200):
 head.train();opt.zero_grad();loss=lossfn(head(x[indices['train']]),y[indices['train']]);loss.backward();opt.step();head.eval()
 with torch.no_grad():vl={s:float(lossfn(head(x[indices[s]]),y[indices[s]])) for s in ['val','mint_dev_val']}
 selection=(vl['val']+vl['mint_dev_val'])/2;history.append({'epoch':epoch+1,'train_loss':float(loss),'val_loss':vl})
 if selection<best:best=selection;state=copy.deepcopy(head.state_dict());stale=0
 else:stale+=1
 if stale>=30:break
head.load_state_dict(state);head.eval();result={}
with torch.no_grad():
 for s,ii in indices.items():
  pred=head(x[ii]).argmax(1);result[s]={'n':len(ii),'correct':int((pred==y[ii]).sum()),'per_class':{sid:{'n':int((y[ii]==j).sum()),'correct':int(((y[ii]==j)&(pred==y[ii])).sum())} for j,sid in enumerate(ids) if (y[ii]==j).any()}}
report={'method':'Fresh ImageNet frozen ConvNeXtTiny features, trained linear10classhead, best mean old/new development-validation loss','results':result,'epochs':len(history),'deployment_ready':False,'caveats':['Development tuning only, not test accuracy','13-photo mint validation is too small and now reused','No old test/new_test or99audit rows extracted','Community labels not expert certified']};(out/'evaluation.json').write_text(json.dumps(report,indent=2));(out/'history.json').write_text(json.dumps(history,indent=2));m.classifier[2]=head;torch.save({'state_dict':m.state_dict(),'species_ids':ids,'architecture':'convnext_tiny','experimental_only':True,'deployment_ready':False,'manifest_sha256':hashlib.sha256(Path(a.manifest).read_bytes()).hexdigest()},out/'experimental.pt');print(json.dumps(report,indent=2))

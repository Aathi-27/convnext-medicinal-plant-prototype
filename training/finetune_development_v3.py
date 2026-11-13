"""Experimental full ConvNeXt-Tiny fine-tuning. Never auto-installs weights.
Train/validation only here; held-out evaluation is a separate explicit step.
"""
import argparse,json,random,hashlib,time
from pathlib import Path
import numpy as np,torch
from torch import nn
from torch.utils.data import Dataset,DataLoader
from torchvision.models import convnext_tiny,ConvNeXt_Tiny_Weights
from torchvision import transforms as T
from torchvision.transforms import InterpolationMode
from PIL import Image,ImageOps
class Leaves(Dataset):
 def __init__(self,rows,train):
  self.rows=rows;ops=[T.Resize((224,224),interpolation=InterpolationMode.BICUBIC)]
  if train:ops += [T.RandomHorizontalFlip(),T.RandomVerticalFlip(),T.RandomRotation(20),T.ColorJitter(.15,.15,.15,.05)]
  self.transform=T.Compose(ops+[T.ToTensor(),T.Normalize([.485,.456,.406],[.229,.224,.225])])
 def __len__(self):return len(self.rows)
 def __getitem__(self,i):
  r=self.rows[i]
  with Image.open(r['path']) as im:x=self.transform(ImageOps.exif_transpose(im).convert('RGB'))
  return x,r['target']
def main():
 p=argparse.ArgumentParser();p.add_argument('--manifest',required=True);p.add_argument('--out',required=True);p.add_argument('--init-checkpoint');p.add_argument('--epochs-this-run',type=int,default=2);a=p.parse_args();out=Path(a.out);out.mkdir(exist_ok=True,parents=True);rows=json.loads(Path(a.manifest).read_text());ids=[r['id'] for r in json.loads((Path(__file__).resolve().parents[1]/'data/species.json').read_text())];digest=hashlib.sha256(Path(a.manifest).read_bytes()).hexdigest();groups={};hashes={}
 for r in rows:
  assert r['content_review']=='provisionally_suitable' and r['review_status']=='experimental_only';assert r['licenseUrl'] in ['https://creativecommons.org/licenses/by-sa/4.0/','https://creativecommons.org/licenses/by/4.0/','https://creativecommons.org/publicdomain/zero/1.0/'];assert r['author'] and r['observationId'];assert hashlib.sha256(Path(r['path']).read_bytes()).hexdigest()==r['sha256'];assert groups.setdefault(r['group'],r['split'])==r['split'];assert hashes.setdefault(r['sha256'],r['split'])==r['split'];r['target']=ids.index(r['species_id'])
 torch.set_num_threads(2);torch.manual_seed(42);random.seed(42);np.random.seed(42)
 model=convnext_tiny(weights=None if (out/'latest.pt').exists() else ConvNeXt_Tiny_Weights.IMAGENET1K_V1);model.classifier[2]=nn.Linear(768,10)
 if a.init_checkpoint and not (out/'latest.pt').exists():
  init=torch.load(a.init_checkpoint,weights_only=False);assert init['species_ids']==ids;model.load_state_dict(init['state_dict'])
 opt=torch.optim.AdamW([{'params':model.features.parameters(),'lr':1e-6},{'params':model.avgpool.parameters(),'lr':1e-6},{'params':model.classifier.parameters(),'lr':2e-5}],weight_decay=.05);lossfn=nn.CrossEntropyLoss(label_smoothing=.05);history=[];start=0;best=float('inf');stale=0
 if (out/'latest.pt').exists():
  c=torch.load(out/'latest.pt',weights_only=False);assert c['manifest_sha256']==digest;model.load_state_dict(c['state_dict']);opt.load_state_dict(c['optimizer']);history=c['history'];start=c['epoch'];best=c['best'];stale=c['stale']
 loaders={s:DataLoader(Leaves([r for r in rows if r['split']==s],s=='train'),batch_size=2,shuffle=s=='train',num_workers=0) for s in ['train','val']};t=time.time()
 for epoch in range(start,min(start+a.epochs_this_run,8)):
  if stale>=4:break
  info={'epoch':epoch+1}
  for split in ['train','val']:
   model.train(split=='train');total=correct=0;ls=0
   with torch.set_grad_enabled(split=='train'):
    for x,y in loaders[split]:
     opt.zero_grad();z=model(x);loss=lossfn(z,y)
     if split=='train':loss.backward();nn.utils.clip_grad_norm_(model.parameters(),1);opt.step()
     total+=len(y);ls+=loss.item()*len(y);correct+=(z.argmax(1)==y).sum().item()
   info[split+'_loss']=ls/total;info[split+'_accuracy']=correct/total
  history.append(info)
  improved=info['val_loss']<best
  if improved:best=info['val_loss'];stale=0
  else:stale+=1
  ck={'state_dict':model.state_dict(),'optimizer':opt.state_dict(),'history':history,'epoch':epoch+1,'best':best,'stale':stale,'manifest_sha256':digest,'species_ids':ids,'architecture':'convnext_tiny','experimental_only':True,'deployment_ready':False}
  torch.save(ck,out/'latest.pt')
  if improved:torch.save({k:v for k,v in ck.items() if k!='optimizer'},out/'best.pt')
  (out/'history.json').write_text(json.dumps(history,indent=2));print(json.dumps(info),flush=True)
 print('elapsed_seconds',round(time.time()-t,1),'stale',stale,flush=True)
if __name__=='__main__':main()

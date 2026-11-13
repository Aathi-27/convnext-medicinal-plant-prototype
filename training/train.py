"""Train only from a reviewed manifest. Never load the legacy augmented split.
Manifest CSV fields: path,species_id,split,group,review_status,photo_license,attribution.
"""
import argparse,csv,json,random,hashlib
from pathlib import Path
import numpy as np
import torch
from torch import nn
from torch.utils.data import Dataset,DataLoader
from torchvision.models import convnext_tiny,ConvNeXt_Tiny_Weights
from torchvision import transforms as T
from torchvision.transforms import InterpolationMode
from PIL import Image,ImageOps
ROOT=Path(__file__).resolve().parents[1]
SPECIES=json.loads((ROOT/'data/species.json').read_text());IDS=[s['id'] for s in SPECIES]
class Leaves(Dataset):
 def __init__(self,rows,training):
  self.rows=rows
  ops=[T.Resize((224,224),interpolation=InterpolationMode.BICUBIC)]
  if training:ops+=[T.RandomHorizontalFlip(),T.RandomVerticalFlip(),T.RandomRotation(30),T.ColorJitter(.3,.3,.3,.1),T.RandomResizedCrop(224,scale=(.7,1),interpolation=InterpolationMode.BICUBIC),T.RandomApply([T.GaussianBlur(3)],p=.15)]
  self.transform=T.Compose(ops+[T.ToTensor(),T.Normalize([.485,.456,.406],[.229,.224,.225])])
 def __len__(self):return len(self.rows)
 def __getitem__(self,i):
  row=self.rows[i]
  with Image.open(row['path']) as im:x=self.transform(ImageOps.exif_transpose(im).convert('RGB'))
  return x,IDS.index(row['species_id'])
def load_manifest(path):
 rows=list(csv.DictReader(open(path,encoding='utf-8')));groups={};hashes={}
 for r in rows:
  assert r['review_status']=='approved','Unreviewed image in training manifest'
  assert r['photo_license'] in {'cc0','cc-by','permissioned'},'Uncleared image rights'
  assert r['attribution'],'Attribution/provenance required'
  assert r['species_id'] in IDS and r['split'] in {'train','val','test'}
  assert r['group'],'A capture/observation group is required'
  assert groups.setdefault(r['group'],r['split'])==r['split'],'Source-group leakage'
  digest=hashlib.sha256(Path(r['path']).read_bytes()).hexdigest()
  assert hashes.setdefault(digest,r['split'])==r['split'],'Exact image leakage'
 for split in ['train','val','test']:
  assert set(r['species_id'] for r in rows if r['split']==split)==set(IDS),f'Every class must be present in {split}'
 return rows

def main():
 p=argparse.ArgumentParser();p.add_argument('--manifest',required=True);p.add_argument('--out',required=True);p.add_argument('--epochs',type=int,default=30);p.add_argument('--batch-size',type=int,default=32);p.add_argument('--seed',type=int,default=42);a=p.parse_args()
 random.seed(a.seed);np.random.seed(a.seed);torch.manual_seed(a.seed)
 rows=load_manifest(a.manifest);device='cuda' if torch.cuda.is_available() else 'cpu';out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
 model=convnext_tiny(weights=ConvNeXt_Tiny_Weights.IMAGENET1K_V1);model.classifier[2]=nn.Linear(768,10);model.to(device)
 loaders={s:DataLoader(Leaves([r for r in rows if r['split']==s],s=='train'),batch_size=a.batch_size,shuffle=s=='train',num_workers=0) for s in ['train','val']}
 opt=torch.optim.AdamW(model.parameters(),lr=1e-4,weight_decay=.05);sched=torch.optim.lr_scheduler.CosineAnnealingLR(opt,a.epochs);lossfn=nn.CrossEntropyLoss();best=float('inf');stale=0;history=[]
 for epoch in range(a.epochs):
  info={'epoch':epoch+1}
  for split in ['train','val']:
   model.train(split=='train');total=correct=0;loss_sum=0.
   with torch.set_grad_enabled(split=='train'):
    for x,y in loaders[split]:
     x,y=x.to(device),y.to(device);opt.zero_grad();z=model(x);loss=lossfn(z,y)
     if split=='train':loss.backward();opt.step()
     total+=len(y);loss_sum+=loss.item()*len(y);correct+=(z.argmax(1)==y).sum().item()
   info[split+'_loss']=loss_sum/total;info[split+'_accuracy']=correct/total
  sched.step();history.append(info);(out/'history.json').write_text(json.dumps(history,indent=2));print(info,flush=True)
  if info['val_loss']<best:
   best=info['val_loss'];stale=0;torch.save({'state_dict':model.cpu().state_dict(),'species_ids':IDS,'architecture':'convnext_tiny','config':vars(a),'manifest_sha256':hashlib.sha256(Path(a.manifest).read_bytes()).hexdigest()},out/'best.pt');model.to(device)
  else:stale+=1
  if stale>=5:break
 (out/'status.json').write_text(json.dumps({'trained':True,'note':'Not deployment-ready until validation threshold, held-out evaluation and ONNX parity are complete.','best_validation_loss':best,'device':device},indent=2))
if __name__=='__main__':main()

"""Internal small-data ConvNeXt-Tiny pipeline pilot. Not a deployment release.
Consumes a provenance-bearing experimental JSON manifest with contributor-group splits.
A community label is not expert botanical verification. No report accuracy is implied.
"""
import argparse,json,hashlib,copy,time
from pathlib import Path
import torch
from torch import nn
from torchvision.models import convnext_tiny,ConvNeXt_Tiny_Weights
from torchvision import transforms as T
from torchvision.transforms import InterpolationMode
from PIL import Image,ImageOps

def main():
 p=argparse.ArgumentParser();p.add_argument('--manifest',required=True);p.add_argument('--out',required=True);a=p.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=True);rows=json.loads(Path(a.manifest).read_text());ids=[s['id'] for s in json.loads((Path(__file__).resolve().parents[1]/'data/species.json').read_text())]
 groups={};hashes={}
 for r in rows:
  assert r['review_status']=='experimental_only' and r['content_review']=='provisionally_suitable'
  assert r['licenseUrl'] in ['https://creativecommons.org/licenses/by-sa/4.0/','https://creativecommons.org/licenses/by/4.0/','https://creativecommons.org/publicdomain/zero/1.0/'] and r['author']
  assert groups.setdefault(r['group'],r['split'])==r['split']
  digest=hashlib.sha256(Path(r['path']).read_bytes()).hexdigest();assert digest==r['sha256'];assert hashes.setdefault(digest,r['split'])==r['split']
 rows=[r for r in rows if r['split'] in ['train','val']]
 for split in ['train','val']:assert {r['species_id'] for r in rows if r['split']==split}==set(ids)
 torch.set_num_threads(2);torch.manual_seed(42);t=time.time();model=convnext_tiny(weights=ConvNeXt_Tiny_Weights.IMAGENET1K_V1);model.classifier[2]=nn.Identity();model.eval()
 prep=T.Compose([T.Resize((224,224),interpolation=InterpolationMode.BICUBIC),T.ToTensor(),T.Normalize([.485,.456,.406],[.229,.224,.225])]);features=[]
 with torch.inference_mode():
  for start in range(0,len(rows),8):
   batch=[]
   for r in rows[start:start+8]:
    with Image.open(r['path']) as im:batch.append(prep(ImageOps.exif_transpose(im).convert('RGB')))
   features.append(model(torch.stack(batch)).clone());print('features',min(start+8,len(rows)),'/',len(rows),flush=True)
 x=torch.cat(features).clone();y=torch.tensor([ids.index(r['species_id']) for r in rows]);indices={s:torch.tensor([i for i,r in enumerate(rows) if r['split']==s]) for s in ['train','val']};head=nn.Linear(768,len(ids));opt=torch.optim.AdamW(head.parameters(),lr=.01,weight_decay=.01);lossfn=nn.CrossEntropyLoss();best=float('inf');best_state=None;history=[];stale=0
 for epoch in range(300):
  head.train();opt.zero_grad();loss=lossfn(head(x[indices['train']]),y[indices['train']]);loss.backward();opt.step();head.eval()
  with torch.no_grad():vl=lossfn(head(x[indices['val']]),y[indices['val']]).item()
  history.append({'epoch':epoch+1,'train_loss':loss.item(),'val_loss':vl})
  if vl<best:best=vl;best_state=copy.deepcopy(head.state_dict());stale=0
  else:stale+=1
  if stale>=30:break
 head.load_state_dict(best_state);head.eval();i=indices['val']
 with torch.no_grad():pred=head(x[i]).argmax(1);correct=(pred==y[i]);conf=torch.softmax(head(x[i]),1).max(1).values
 matrix=[[0]*10 for _ in ids]
 for truth,guess in zip(y[i].tolist(),pred.tolist()):matrix[truth][guess]+=1
 report={'deployment_ready':False,'experimental_only':True,'architecture':'convnext_tiny','training_scope':'ImageNet pretrained frozen ConvNeXt feature extractor, newly trained linear head; no full fine-tuning','dataset_note':'Small visually screened community-labeled photos, not expert-certified, not report dataset, not an external phone-image benchmark','evaluation_scope':'Development validation only; all old test/new_test rows excluded before feature extraction','selected_count':len(rows),'validation_count':len(i),'validation_correct':int(correct.sum()),'validation_accuracy':correct.float().mean().item(),'per_class_validation_support':{s:int((y[i]==j).sum()) for j,s in enumerate(ids)},'confusion_matrix':matrix,'species_ids':ids,'validation_best_loss':best,'manifest_sha256':hashlib.sha256(Path(a.manifest).read_bytes()).hexdigest(),'elapsed_seconds':round(time.time()-t,2),'epochs':len(history),'caveats':['Too little data for reliable class-wise accuracy or rejection calibration.','Community labels may be wrong; mint hybrids are visually difficult.','No deployment, medicinal-use or safety claim.','No augmentation counted as additional original images.']}
 model.classifier[2]=head;torch.save({'state_dict':model.state_dict(),'architecture':'convnext_tiny','species_ids':ids,'experimental_only':True,'deployment_ready':False,'report':report},out/'experimental.pt');(out/'evaluation.json').write_text(json.dumps(report,indent=2));(out/'history.json').write_text(json.dumps(history,indent=2));print(json.dumps(report,indent=2),flush=True)
if __name__=='__main__':main()

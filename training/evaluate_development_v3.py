"""One explicit evaluation of a frozen checkpoint on named internal holdouts."""
import json,hashlib,collections,argparse
from pathlib import Path
import torch,numpy as np
from torchvision.models import convnext_tiny
from finetune_experiment import Leaves
from torch.utils.data import DataLoader
p=argparse.ArgumentParser();p.add_argument('--manifest',required=True);p.add_argument('--checkpoint-dir',required=True);a=p.parse_args();out=Path(a.checkpoint_dir);torch.set_num_threads(2);c=torch.load(out/'best.pt',weights_only=False);rows=json.load(open(a.manifest));ids=c['species_ids'];model=convnext_tiny();model.classifier[2]=torch.nn.Linear(768,10);model.load_state_dict(c['state_dict']);model.eval();results={}
for split in ['val']:
 rr=[dict(r,target=ids.index(r['species_id'])) for r in rows if r['split']==split];cm=np.zeros((10,10),int);predictions=[]
 with torch.inference_mode():
  for i,(x,y) in enumerate(DataLoader(Leaves(rr,False),batch_size=1)):
   prob=torch.softmax(model(x),1)[0];pred=int(prob.argmax());actual=int(y);cm[actual,pred]+=1;predictions.append({'photo_id':rr[i]['id'],'actual':ids[actual],'predicted':ids[pred],'score':float(prob[pred])})
 results[split]={'n':int(cm.sum()),'correct':int(np.trace(cm)),'accuracy':float(np.trace(cm)/cm.sum()),'confusion_matrix':cm.tolist(),'per_class':{s:{'correct':int(cm[i,i]),'total':int(cm[i].sum())} for i,s in enumerate(ids)},'predictions':predictions}
report={'architecture':'convnext_tiny','method':'Frozen-feature head initialization on expanded training set, then8epochs full fine-tuning batch2 with lower backbone learning rate; best development validation-loss checkpoint','checkpoint_epoch':c['epoch'],'checkpoint_sha256':hashlib.sha256((out/'best.pt').read_bytes()).hexdigest(),'manifest_sha256':c['manifest_sha256'],'experimental_only':True,'deployment_ready':False,'caveats':['Community labels, not expert-certified','Small internal contributor-grouped holdouts, not external phone benchmark','All old heldout sets excluded; development validation only','No report accuracy reproduction or calibrated reliability claim'],'species_ids':ids,'results':results};(out/'evaluation.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:{a:b for a,b in v.items() if a not in ['predictions','confusion_matrix']} for k,v in results.items()},indent=2))

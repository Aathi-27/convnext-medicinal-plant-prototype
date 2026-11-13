import io,json,hashlib,os
from pathlib import Path
import numpy as np
from PIL import Image,ImageOps,UnidentifiedImageError
ROOT=Path(__file__).resolve().parents[1]
SPECIES=json.loads((ROOT/'data/species.json').read_text())
MAX_BYTES=10*1024*1024
Image.MAX_IMAGE_PIXELS=10_000_000
class InputError(ValueError):pass

def preprocess(raw:bytes):
 if not raw or len(raw)>MAX_BYTES:raise InputError('Choose an image smaller than 10 MB.')
 try:
  with Image.open(io.BytesIO(raw)) as source:
   if source.format not in {'JPEG','PNG','WEBP'}:raise InputError('Use a JPEG, PNG or WebP photo.')
   if source.width*source.height>10_000_000:raise InputError('Image exceeds 10 megapixels.')
   if min(source.size)<32:raise InputError('Photo is too small. Use a clearer leaf image.')
   image=ImageOps.exif_transpose(source).convert('RGB').resize((224,224),Image.Resampling.BICUBIC)
   arr=np.asarray(image,dtype=np.float32)/255
 except (UnidentifiedImageError,OSError,Image.DecompressionBombError,Image.DecompressionBombWarning) as e:raise InputError('This file cannot be read safely as an image.') from e
 arr=(arr-np.array([.485,.456,.406],dtype=np.float32))/np.array([.229,.224,.225],dtype=np.float32)
 return np.transpose(arr,(2,0,1))[None].copy()

class Classifier:
 def __init__(self,directory):
  self.directory=Path(directory);self.session=None;self.meta=None
  config=self.directory/'model.json'
  if not config.exists():return
  self.meta=json.loads(config.read_text());model=self.directory/self.meta['file']
  if self.meta.get('architecture')!='convnext_tiny' or not self.meta.get('trained'):raise ValueError('Only a trained ConvNeXt-Tiny artifact is accepted.')
  if self.meta.get('species_ids')!=[s['id'] for s in SPECIES]:raise ValueError('Model class order must match the species registry.')
  if hashlib.sha256(model.read_bytes()).hexdigest()!=self.meta['sha256']:raise ValueError('Model checksum mismatch.')
  if not isinstance(self.meta.get('confidence_threshold'),(int,float)):raise ValueError('Validation-derived threshold is missing.')
  import onnxruntime as ort
  opt=ort.SessionOptions();opt.intra_op_num_threads=1;opt.inter_op_num_threads=1;opt.enable_cpu_mem_arena=False
  self.session=ort.InferenceSession(str(model),sess_options=opt,providers=['CPUExecutionProvider'])
 def predict(self,image):
  logits=self.session.run(None,{'image':image})[0][0]
  probs=np.exp(logits-np.max(logits));probs/=probs.sum();order=np.argsort(probs)[::-1]
  results=[{**SPECIES[int(i)],'score':float(probs[i])} for i in order[:3]]
  uncertain=results[0]['score']<self.meta['confidence_threshold']
  return {'status':'uncertain' if uncertain else 'candidate','candidates':results,'model_version':self.meta['version'],'warning':'A model score is not proof of identity. Do not consume or use a plant based on this prediction.'}

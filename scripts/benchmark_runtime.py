"""Architecture/runtime benchmark only. Untrained 10-class head, never for predictions."""
import json,time,resource,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
if sys.argv[1]=='export':
 import torch
 from torchvision.models import convnext_tiny
 torch.set_num_threads(1)
 model=convnext_tiny(weights=None).eval()
 model.classifier[2]=torch.nn.Linear(768,10)
 torch.onnx.export(model,torch.zeros(1,3,224,224),str(ROOT/'artifacts/architecture-benchmark.onnx'),opset_version=17,input_names=['image'],output_names=['logits'])
 print('exported untrained architecture benchmark')
else:
 import onnxruntime as ort,psutil
 start=time.perf_counter();opt=ort.SessionOptions();opt.intra_op_num_threads=1;opt.inter_op_num_threads=1
 opt.enable_cpu_mem_arena=False
 session=ort.InferenceSession(str(ROOT/'artifacts/architecture-benchmark.onnx'),sess_options=opt,providers=['CPUExecutionProvider'])
 loaded=time.perf_counter()-start
 values=[]
 for i in range(5):
  t=time.perf_counter();session.run(None,{'image':np.zeros((1,3,224,224),dtype=np.float32)});values.append(time.perf_counter()-t)
 print(json.dumps({'benchmark_only':True,'trained':False,'load_seconds':loaded,'inference_seconds':values,'rss_mb':psutil.Process().memory_info().rss/1024**2,'peak_rss_mb':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,'onnx_mb':(ROOT/'artifacts/architecture-benchmark.onnx').stat().st_size/1024**2},indent=2))

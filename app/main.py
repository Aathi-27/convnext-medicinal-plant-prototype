import asyncio,os,json
from fastapi import FastAPI,UploadFile,HTTPException,Form,Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from . import external
from .core import Classifier,preprocess,InputError,MAX_BYTES,ROOT,SPECIES
app=FastAPI(title='Medicinal Plant Research Prototype',version='0.1.0')
classifier=Classifier(os.getenv('MODEL_DIR',str(ROOT/'artifacts')))
lock=asyncio.Semaphore(1)
@app.get('/api/health')
def health():return {'ok':True,'model_ready':classifier.session is not None,'architecture':'convnext_tiny','experimental':classifier.experimental,'external_fallback_enabled':external.enabled()}
@app.get('/api/species')
def species():return SPECIES
@app.post('/api/predict')
async def predict(file:UploadFile):
 async with lock:
  raw=await file.read(MAX_BYTES+1)
  try:image=await asyncio.to_thread(preprocess,raw)
  except InputError as e:raise HTTPException(422,str(e))
  if classifier.session is None:raise HTTPException(503,'The trained model is not ready. No prediction has been generated.')
  result=await asyncio.to_thread(classifier.predict,image)
 return result
@app.post('/api/external-suggestion')
async def external_suggestion(request:Request,file:UploadFile,consent:bool=Form(False),predicted_common:str=Form(''),predicted_scientific:str=Form('')):
 if not consent:raise HTTPException(400,'Explicit consent is required before sending this photo to an external service.')
 if request.headers.get('sec-fetch-site')=='cross-site':raise HTTPException(403,'Open the demo directly to request an external check.')
 if not external.enabled():raise HTTPException(503,'External checks are not enabled. Local results are unchanged.')
 raw=await file.read(MAX_BYTES+1)
 try:
  photo=await asyncio.to_thread(external.prepare_photo,raw)
  return await asyncio.to_thread(external.explain,photo,predicted_common,predicted_scientific)
 except InputError as e:raise HTTPException(422,str(e))
 except external.ExternalError as e:raise HTTPException(e.status,e.message)
@app.get('/api/knowledge/{species_id}')
def knowledge(species_id:str):
 records=json.loads((ROOT/'data/knowledge.json').read_text())
 if species_id not in records:raise HTTPException(404,'Unknown species.')
 return records[species_id]
if (ROOT/'web/dist').exists():
 app.mount('/assets',StaticFiles(directory=ROOT/'web/dist/assets'),name='assets')
 @app.get('/botanical.webp')
 def botanical():return FileResponse(ROOT/'web/dist/botanical.webp')
 @app.get('/')
 def index():return FileResponse(ROOT/'web/dist/index.html')

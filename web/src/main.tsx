import React,{useEffect,useRef,useState} from 'react';
import{createRoot}from'react-dom/client';import'./style.css';
type Species={id:string;common_name:string;scientific_name:string};
type Candidate=Species&{score:number};
type Knowledge={common_name:string;scientific_name:string;review_status:string;notice:string;safety_notes:string[];sources:{url:string;title:string}[];traditional_uses:string[];constituents:string[];names:{tamil:string|null;sanskrit:string|null}};
type Result={experimental?:boolean;status:string;candidates:Candidate[];warning:string;model_version:string;knowledge?:Knowledge};
function KnowledgeDetails({record}:{record:Knowledge}){return <><p className="notice">{record.notice}</p><h4>Traditional use & evidence</h4>{record.traditional_uses.map(t=><p key={t}>{t}</p>)}{record.constituents.length>0&&<><h4>Reported constituents</h4><p>{record.constituents.join(', ')}. A photo cannot confirm composition.</p></>}<h4>Safety</h4><ul>{record.safety_notes.map(t=><li key={t}>{t}</li>)}</ul><h4>Sources</h4>{record.sources.map(s=><p key={s.url}><a href={s.url} target="_blank" rel="noreferrer">{s.title} ↗</a></p>)}<p className="small">Partial source review. Not medical advice. {record.names.tamil?'Tamil: '+record.names.tamil+'. ':''}Regional names not shown are still unverified.</p></>}
type ExternalResult={status:string;suggestion:{scientific_name:string;common_name:string;confidence_label:string;uncertainty:string;visible_features:string[]};warning:string};
function App(){
 const[externalEnabled,setExternalEnabled]=useState(false);const[externalBusy,setExternalBusy]=useState(false);const[externalError,setExternalError]=useState('');const[externalResult,setExternalResult]=useState<ExternalResult|null>(null);const externalRequest=useRef(0);
 const[file,setFile]=useState<File|null>(null);const[preview,setPreview]=useState('');const[resizeNote,setResizeNote]=useState('');const[busy,setBusy]=useState(false);const[error,setError]=useState('');const[result,setResult]=useState<Result|null>(null);const[ready,setReady]=useState<boolean|null>(null);const[experimental,setExperimental]=useState(false);const[resultRecord,setResultRecord]=useState<Knowledge|null>(null);const[species,setSpecies]=useState<Species[]>([]);const[library,setLibrary]=useState(false);const[record,setRecord]=useState<Knowledge|null>(null);const[knowledgeError,setKnowledgeError]=useState('');const libraryRequest=useRef(0);const candidateRequest=useRef(0);const input=useRef<HTMLInputElement>(null);const camera=useRef<HTMLInputElement>(null);
 useEffect(()=>{fetch('/api/health').then(r=>r.json()).then(x=>{setReady(x.model_ready);setExternalEnabled(x.external_fallback_enabled===true);setExperimental(x.experimental===true)}).catch(()=>setReady(null));fetch('/api/species').then(r=>r.json()).then(setSpecies).catch(()=>{});},[]);
 useEffect(()=>()=>{if(preview)URL.revokeObjectURL(preview)},[preview]);
 async function downscale(f:File):Promise<{file:File,resized:boolean}>{
  let source:ImageBitmap|HTMLImageElement;
  try{source=await createImageBitmap(f)}catch{source=await new Promise<HTMLImageElement>((resolve,reject)=>{const url=URL.createObjectURL(f);const img=new Image();img.onload=()=>{URL.revokeObjectURL(url);resolve(img)};img.onerror=()=>{URL.revokeObjectURL(url);reject(new Error('decode'))};img.src=url})}
  const width=source instanceof HTMLImageElement?source.naturalWidth:source.width;
  const height=source instanceof HTMLImageElement?source.naturalHeight:source.height;
  if(!width||!height)throw new Error('decode');
  if(width*height<=8_000_000&&f.size<=8*1024*1024){if('close' in source)(source as ImageBitmap).close();return{file:f,resized:false}}
  const scale=Math.min(1,Math.sqrt(4_000_000/(width*height)),2560/Math.max(width,height));
  const canvas=document.createElement('canvas');canvas.width=Math.max(1,Math.round(width*scale));canvas.height=Math.max(1,Math.round(height*scale));
  const ctx=canvas.getContext('2d');if(!ctx)throw new Error('canvas');
  ctx.drawImage(source,0,0,canvas.width,canvas.height);
  if('close' in source)(source as ImageBitmap).close();
  const blob=await new Promise<Blob|null>(resolve=>canvas.toBlob(resolve,'image/jpeg',0.88));
  if(!blob)throw new Error('encode');
  return{file:new File([blob],f.name.replace(/\.[^.]+$/,'')+'.jpg',{type:'image/jpeg'}),resized:true};
 }
 async function select(f:File|undefined){if(!f||busy||externalBusy)return;++externalRequest.current;setExternalResult(null);setExternalError('');setExternalBusy(false);++candidateRequest.current;setResult(null);setResultRecord(null);setError('');setResizeNote('');if(!['image/jpeg','image/png','image/webp'].includes(f.type)){setError('Use a JPEG, PNG or WebP photo.');return}try{const prepared=await downscale(f);setFile(prepared.file);setPreview(URL.createObjectURL(prepared.file));if(prepared.resized)setResizeNote('Large photo resized automatically for analysis. The original stays on your device.')}catch{setError('This file could not be read as an image. Try a different photo.')}}
 async function openRecord(id:string){const request=++libraryRequest.current;setRecord(null);setKnowledgeError('');try{const r=await fetch('/api/knowledge/'+id);if(!r.ok)throw new Error('Plant information could not load.');const data=await r.json();if(request===libraryRequest.current)setRecord(data)}catch{if(request===libraryRequest.current)setKnowledgeError('Plant information could not load. Please retry.')}}
 async function reviewCandidate(id:string){const request=++candidateRequest.current;setResultRecord(null);setError('');try{const r=await fetch('/api/knowledge/'+id);if(!r.ok)throw new Error();const data=await r.json();if(request===candidateRequest.current)setResultRecord(data)}catch{if(request===candidateRequest.current)setError('Plant notes could not load. Please retry.')}}
 async function analyze(){if(!file)return;const photo=file;++externalRequest.current;setExternalResult(null);setExternalError('');++candidateRequest.current;setResultRecord(null);setBusy(true);setError('');setResult(null);const controller=new AbortController();const timeout=setTimeout(()=>controller.abort(),120000);try{const body=new FormData();body.append('file',photo);const response=await fetch('/api/predict',{method:'POST',body,signal:controller.signal});const data=await response.json();if(!response.ok)throw new Error(data.detail||'Analysis could not finish.');setResult(data);if(externalEnabled&&(data.candidates?.[0]?.score??1)<0.70)await externalCheck(photo)}catch(e){setError(e instanceof Error?(e.name==='AbortError'?'The server took too long. A free server may be waking up. Please retry.':e.message):'Could not connect. Please retry.')}finally{setBusy(false);clearTimeout(timeout)}}
 async function externalCheck(photo:File){if(externalBusy)return;const request=++externalRequest.current;setExternalBusy(true);setExternalError('');setExternalResult(null);const controller=new AbortController();const timeout=setTimeout(()=>controller.abort(),35000);try{const body=new FormData();body.append('file',photo);body.append('consent','true');const response=await fetch('/api/external-suggestion',{method:'POST',body,signal:controller.signal});const data=await response.json();if(!response.ok)throw new Error(typeof data.detail==='string'?data.detail:'External check could not finish.');if(request===externalRequest.current){setExternalResult(data);setResultRecord(null);++candidateRequest.current;}}catch(e){if(request===externalRequest.current)setExternalError(e instanceof Error?(e.name==='AbortError'?'The second check took too long. Showing the local candidates.':e.message):'The second check could not finish. Showing the local candidates.')}finally{clearTimeout(timeout);if(request===externalRequest.current)setExternalBusy(false)}}
 const displayedCandidates:Candidate[]=externalResult?[{id:species.find(s=>s.scientific_name===externalResult.suggestion.scientific_name)?.id??'',common_name:externalResult.suggestion.common_name,scientific_name:externalResult.suggestion.scientific_name,score:NaN}]:(result?.candidates??[]);const hasNotes=displayedCandidates.some(c=>!!c.id);
 return <><div className="top">Medicinal plant identification · a research prototype</div><header><div className="logo">Leaf study<small>PLANT IMAGES · KNOWLEDGE NOTES</small></div><nav className="nav" aria-label="Main navigation"><button className="item" onClick={()=>setLibrary(false)}>Identify a plant</button><button className="item" onClick={()=>setLibrary(!library)}>Plant library</button><span className="tag">RESEARCH PROTOTYPE</span></nav></header><section className="hero"><img src="/botanical.webp" alt="Illustrative botanical artwork, not a species identification guide"/><div className="hero-copy"><div className="eyebrow">From a leaf to understanding</div><h1>Every leaf has<br/>a story.<br/>Start with a photo.</h1><p>Explore plant identity through computer vision and source-linked botanical knowledge.</p></div><div className="art">Illustrative botanical artwork</div></section>
 {library&&<section className="library"><h2>Supported species</h2><div className="library-grid">{species.map(s=><button className="library-item" onClick={()=>openRecord(s.id)} key={s.id}>{s.common_name}<small>{s.scientific_name}</small></button>)}</div><p className="small">Choose a plant to read source-linked educational notes. These records do not require a model prediction.</p>{knowledgeError&&<p role="alert">{knowledgeError}</p>}{record&&<article className="knowledge"><h3>{record.common_name}</h3><em>{record.scientific_name}</em><KnowledgeDetails record={record}/></article>}<p className="small">A species list is not evidence that a model has finished training. Check the model status below.</p></section>}
 <main className="workspace">
<section className="panel">
<div className="sectionline">
<h2>Identify your leaf</h2>
<span className="step">01 / UPLOAD</span>
</div>
<div className="upload" onDragOver={e=>e.preventDefault()} onDrop={e=>{e.preventDefault();select(e.dataTransfer.files[0])}}>{preview?<img className="preview" src={preview} alt="Your selected leaf photograph"/>:<div>
<div className="symbol">↑</div>
<strong>Bring a leaf into focus</strong>
<p className="small">Drop a photo here, or choose a file.<br/>One leaf · clear light · simple background</p>
</div>}</div>
<input hidden ref={input} type="file" accept="image/jpeg,image/png,image/webp" onChange={e=>select(e.target.files?.[0])}/>
<input hidden ref={camera} type="file" accept="image/*" capture="environment" onChange={e=>select(e.target.files?.[0])}/>
<div className="actions">
<button className="button" onClick={()=>input.current?.click()} disabled={busy||externalBusy}>Choose a photo ↗</button>
<button className="button secondary" onClick={()=>camera.current?.click()} disabled={busy||externalBusy}>Use camera</button>
</div>{file&&<>{resizeNote&&<p className="small">{resizeNote}</p>}<p className="crop-note">Review your photo: keep one complete leaf visible. Automatic segmentation and in-app crop adjustment are not enabled yet.</p>
<button className="button" onClick={analyze} disabled={busy||externalBusy}>{busy?'Analyzing…':'Analyze leaf'}</button>
</>}<p className="privacy">Photos are processed using AI services.</p>
<p className="status" role="status">{ready===false?'Model status: trained checkpoint not ready. No predictions will be invented.':ready===true?(experimental?'Model status: experimental checkpoint. Identification is unverified.':'Model status: trained checkpoint loaded.'):'Connecting to the research server…'}</p>{error&&<p className="status error" role="alert">{error}</p>}<div className="steps">
<div className="mini">Review your photo<span>Keep the full leaf visible.</span>
</div>
<div className="mini">Read with context<span>A prediction is not a confirmed identification.</span>
</div>
</div>
</section>
 <section className="panel result" aria-live="polite">
<div className="sectionline">
<h2>Your plant, explained</h2>
<span className="step">02 / RESULT</span>
</div>
<div className="empty">{busy?<>
<div className="leaf-icon">❧</div>
<h3>Taking a closer look.</h3>
<p>Checking the leaf photo. Free hosting can take longer after inactivity.</p>
</>:result?<div className="results">
<h3>Possible matches</h3>
<p className="notice">{externalResult?'Possible match, not a confirmed species.':result.status==='uncertain'?'Uncertain result. Try another clear photo.':'Possible match, not a confirmed species.'}</p>{externalBusy&&<p className="small">Taking a closer look…</p>}{externalError&&<p className="error" role="alert">{externalError}</p>}{displayedCandidates.map((c,i)=>
<div className="candidate" key={c.id}>
<div>{i+1}. {c.common_name}<small>{c.scientific_name}</small>
<>{c.id&&<button className="button secondary" onClick={()=>reviewCandidate(c.id)}>Read notes about this possible match</button>}</>
</div>{!externalResult&&<span>{(c.score*100).toFixed(1)}%</span>}</div>)}<p className="small">{externalResult?"Photo checked by the external AI service under the Analyze-leaf notice. AI self-ratings are not measured certainty.":"Local model scores are not calibrated certainty or proof of identity."}</p>{externalResult&&<>
<p>{externalResult.suggestion.uncertainty}</p>
<ul>{externalResult.suggestion.visible_features.map((x,i)=>
<li key={i}>{x}</li>)}</ul>
</>}<p className="notice">{!externalResult&&result.experimental?'Experimental model: generalization checks failed. These are research candidates only. ':''}Plant identity is not confirmed. {hasNotes?'Choose a possible match above to read educational notes. These are not a recommendation to use your photographed plant.':'No matching notes are available for this suggestion. Try another clear photo or browse the plant library separately.'}</p>{resultRecord&&<article className="knowledge">
<h3>Notes about {resultRecord.common_name}</h3>
<em>{resultRecord.scientific_name}</em>
<p className="notice">These notes describe the selected species. They do not confirm that your photo shows this plant. Do not consume or treat with it based on this result.</p>
<KnowledgeDetails record={resultRecord}/>
</article>}<p className="small">{externalResult?externalResult.warning:result.warning}</p>
{!externalResult&&<p className="small">{"Local model: "+result.model_version}</p>}</div>:<>
<div className="leaf-icon">❧</div>
<h3>A closer look starts here.</h3>
<p>After analysis, review possible matches and source-linked educational notes.</p>
</>}</div>
<div className="chips">
<span className="chip">Botanical identity</span>
<span className="chip">Traditional knowledge</span>
<span className="chip">Sources & safety</span>
</div>
</section>
</main>
<footer className="foot">
<span>ConvNeXt-Based Medicinal Plant Identification and Knowledge Retrieval</span>
<span>Identification aid only. Not medical advice.</span>
</footer>
<div className="concept">EXPERIMENTAL DEMO · PLANT IDENTITIES ARE UNVERIFIED</div>
</>;
}
createRoot(document.getElementById('root')!).render(<App/>);

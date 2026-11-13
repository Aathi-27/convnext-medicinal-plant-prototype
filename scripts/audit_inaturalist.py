"""Collect metadata only. Each image still needs a leaf-content and label review.
No claim that research grade makes an image a leaf-only classification example.
Only photo-specific CC0/CC-BY licenses accepted; retain author and license.
"""
import json, time, urllib.parse, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ALLOWED={'cc0','cc-by'}
def get(path,params):
 url='https://api.inaturalist.org/v1/'+path+'?'+urllib.parse.urlencode(params)
 req=urllib.request.Request(url,headers={'User-Agent':'MedicinalPlantResearchPrototype/0.1 (dataset provenance audit)'})
 with urllib.request.urlopen(req,timeout=40) as r: data=json.load(r)
 time.sleep(1.2)
 return data

def main():
 out=[]
 for species in json.loads((ROOT/'data/species.json').read_text()):
  name=species['scientific_name'].replace('×','x')
  matches=get('taxa',{'q':name,'per_page':10})['results']
  match=next((t for t in matches if t['name'].replace('×','x').lower()==name.lower()),None)
  if not match:
   print(species['id'],'NO EXACT TAXON MATCH',flush=True);continue
  data=get('observations',{'taxon_id':match['id'],'quality_grade':'research','photos':'true','photo_license':'cc0,cc-by','per_page':100,'order_by':'created_at','order':'desc'})
  records=[]
  for obs in data['results']:
   if obs.get('taxon',{}).get('id')!=match['id']:continue
   for photo in obs.get('photos',[]):
    if photo.get('license_code') not in ALLOWED:continue
    records.append({'species_id':species['id'],'scientific_name':species['scientific_name'],'taxon_id':match['id'],'observation_id':obs['id'],'observation_url':obs['uri'],'photo_id':photo['id'],'photo_url':photo['url'],'license':photo['license_code'],'attribution':photo.get('attribution',''),'observer_id':obs['user']['id'],'observed_on':obs.get('observed_on'),'review_status':'pending','split_group':str(obs['id'])})
    break
  entry={'species':species,'taxon_id':match['id'],'api_candidate_observation_count':data['total_results'],'records':records}
  out.append(entry)
  (ROOT/'data/candidate_manifest.json').write_text(json.dumps(out,indent=2,ensure_ascii=False))
  print(species['id'], 'taxon',match['id'],'candidate observations',data['total_results'],'eligible metadata',len(records),flush=True)
if __name__=='__main__':main()

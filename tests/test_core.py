import io,json
from PIL import Image
import numpy as np
import pytest
from app.core import preprocess,InputError,Classifier,ROOT,SPECIES

def image(mode='RGB',size=(300,200)):
 b=io.BytesIO();Image.new(mode,size,'white').save(b,format='PNG');return b.getvalue()
def test_preprocess_shape():
 x=preprocess(image());assert x.shape==(1,3,224,224);assert x.dtype==np.float32
 assert np.isfinite(x).all()
def test_bad_file():
 with pytest.raises(InputError):preprocess(b'not a photo')
def test_small():
 with pytest.raises(InputError):preprocess(image(size=(4,4)))
def test_oversize():
 with pytest.raises(InputError):preprocess(b'x'*(10*1024*1024+1))
def test_missing_model_does_not_predict(tmp_path):assert Classifier(tmp_path).session is None
def test_species_and_knowledge():
 k=json.loads((ROOT/'data/knowledge.json').read_text());assert len(SPECIES)==10;assert set(k)=={s['id'] for s in SPECIES}
 assert k['brahmi']['scientific_name']=='Bacopa monnieri'
def test_untrained_model_rejected(tmp_path):
 (tmp_path/'model.json').write_text(json.dumps({'architecture':'convnext_tiny','trained':False,'file':'bad.onnx'}))
 with pytest.raises(ValueError):Classifier(tmp_path)

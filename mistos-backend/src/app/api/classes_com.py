from pydantic import BaseModel, constr
from typing import List, Optional, Set
import app.api.utils_classes as utils_classes
   
    
class ComImageResultLayer(BaseModel):
    uid: int
    name: str
    hint: str
    imageId: int
    imageChannel: int  
    layerType: constr(regex = utils_classes.layer_type_regex)
        
        
class ComImage(BaseModel):
    uid: int
    metadata: dict
    hint: Optional[str]
    experimentIds: Optional[List[int]] = []
    imageResultLayers: Optional[List[ComImageResultLayer]]
    tags: Set[str] = set()
        
class ComExperimentGroup(BaseModel):
    uid: int
    experimentId: int
    name: str
    hint: Optional[str]
    description: Optional[str]
    images: Optional[List[ComImage]] = []

class ComExperimentResult(BaseModel):
    uid: int
    description: str
    experimentGroups: List[ComExperimentGroup]
    activeImageIds: List[int]
    activeImageResultLayerIds: List[int]
    resultType: constr(regex = utils_classes.layer_type_regex)
    
class ComExperiment(BaseModel):
    uid: int
    name: str
    hint: str
    description: str
    tags: Set[str] = set()
    experimentGroups: Optional[List[ComExperimentGroup]] = []
    activeImageIds: Optional[List[int]] = []
    activeImageResultLayerIds: Optional[List[int]] = []
    experimentResult: Optional[ComExperimentResult]
    
    
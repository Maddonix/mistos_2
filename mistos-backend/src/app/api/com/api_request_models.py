from typing import Optional
from pydantic import BaseModel
from typing import List, Any
import app.api.classes_com as c_com

# General
class UpdateHintRequest(BaseModel):
    id: int
    new_hint: str

class UpdateDescriptionRequest(BaseModel):
    id: int
    new_description: str

class UpdateNameRequest(BaseModel):
    id: int
    new_name:str

class DeleteRequest(BaseModel):
    id: int

# Images
class ViewImageRequest(BaseModel):
    image_id: int
    display_result_layers: bool
    display_background_layers:bool

class UpdateChannelNamesRequest(BaseModel):
    image_id: int
    channel_names: List[str]

# Experiments
class CreateExperimentRequest(BaseModel):
    experiment: c_com.ComExperiment

class NewExperimentGroupRequest(BaseModel):
    experiment_id: int

class CalculateExperimentResultsRequest(BaseModel):
    experiment_id:int

class DeleteExperimentGroupRequest(BaseModel):
    experiment_id: int
    group_id: int

class DeleteExperimentRequest(BaseModel):
    experiment_id:int

class UpdateExperimentGroupImagesRequest(BaseModel):
    group_id:int
    image_id_list:List[int]

class DeleteImageFromExperimentGroupRequest(BaseModel):
    group_id: int
    image_id: int

class AddLayerToGroupRequest(BaseModel):
    group_id: int
    layer_id: int

class ExportExperimentRequest(BaseModel):
    experiment_id: int
    export_request: dict
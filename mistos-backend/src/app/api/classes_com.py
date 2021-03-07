# pylint:disable=no-name-in-module, import-error
from pydantic import BaseModel, constr
from typing import List, Optional, Set, Dict
from app.api import cfg_classes
from app.api import classes_db as c_db


class ComImageResultLayer(BaseModel):
    uid: int
    name: str
    hint: str
    imageId: int
    layerType: str

    def on_init(self):
        pass


class ComResultMeasurement(BaseModel):
    uid: int
    name: str
    hint: str = ""
    imageId: int
    resultLayerId: int
    measurement_summary: dict

    def on_init(self):
        pass


class ComImage(BaseModel):
    uid: int
    seriesIndex: int
    name: str = ""
    hasBgLayer: bool = False
    bgLayerId: Optional[int]
    metadata: dict  # define exactly what we need: channel names, x, y, scale
    hint: str = ""
    imageResultLayers: List[ComImageResultLayer] = []
    measurements: List[ComResultMeasurement]
    tags: List[str] = []

    def on_init(self):
        self.tags = list(self.tags)
        pass


class ComExperimentGroup(BaseModel):
    uid: int
    experimentId: int
    name: str
    hint: str = ""
    description: str = ""
    images: List[ComImage] = []
    resultLayerIds: List[int] = []


class ComExperimentResult(BaseModel):
    uid: int
    hint: str
    name: str
    description: str
    experimentGroupIds: List[int]
    resultType: str


class ComExperiment(BaseModel):
    uid: int
    name: str
    hint: str
    description: str
    tags: List[str]
    experimentGroups: List[ComExperimentGroup] = []

    def to_db_class(self):
        kwargs = self.dict()

        return c_db.DbExperiment(**kwargs)


class ComClassifier(BaseModel):
    uid: int
    name: str = ""
    clfType: constr(regex=cfg_classes.classifier_type_regex)
    params: dict = {}
    metrics: dict = {}
    tags: List[str] = []

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, PickleType
from sqlalchemy.schema import Table
from sqlalchemy.orm import relationship

from .database import Base

experiment_groups_images_association_table = Table(
    "experiment_groups_images_association_table",
    Base.metadata,
    Column("experiment_group_ids", ForeignKey("experiment_group.id")),
    Column("image_ids", ForeignKey("image.id"))
)

experiment_groups_result_layers_association_table = Table(
    "experiment_groups_result_layers_association_table",
    Base.metadata,
    Column("experiment_group_ids", ForeignKey("experiment_group.id")),
    Column("result_layers_ids", ForeignKey("result_layer.id"))
)

experiment_groups_measurements_association_table = Table(
    "experiment_groups_measurements_association_table",
    Base.metadata,
    Column("experiment_group_ids", ForeignKey("experiment_group.id")),
    Column("measurements_ids", ForeignKey("measurement.id"))
)

class Image(Base):
    __tablename__ = "image"

    id = Column(Integer, primary_key=True, index = True)
    name = Column(String, nullable=False, index = True)
    series_index = Column(Integer, nullable = False)
    path_image = Column(String)
    path_metadata = Column(String)
    hint = Column(String)
    tags = Column(PickleType)
    has_bg_layer = Column(Boolean)
    bg_layer_id = Column(Integer)

    # One to Many
    result_layers = relationship("ResultLayer", back_populates = "image")
    measurements = relationship("Measurement", back_populates = "image")

    # Many to Many
    experiment_groups = relationship(
        "ExperimentGroup",
        secondary= experiment_groups_images_association_table,
        back_populates = "images"
    )

class ResultLayer(Base):
    __tablename__ = "result_layer"

    id = Column(Integer, primary_key=True, index = True)
    path = Column(String)
    name = Column(String)
    hint = Column(String)
    layer_type = Column(String)

    # One to Many
    ## One result layer to many Measurements
    measurements = relationship("Measurement", back_populates = "result_layer")

    # Many to One
    ## result layer has only one image
    image_id = Column(Integer, ForeignKey("image.id"))
    image = relationship("Image", back_populates = "result_layers", cascade="all, delete-orphan", single_parent=True)

    # Many to Many
    experiment_groups = relationship(
        "ExperimentGroup",
        secondary= experiment_groups_result_layers_association_table,
        back_populates = "result_layers"
    )
    
class Measurement(Base):
    __tablename__ = "measurement"

    id = Column(Integer, primary_key=True, index = True)
    path = Column(String)
    name = Column(String)
    hint = Column(String)

    # Many to One
    result_layer_id = Column(Integer, ForeignKey("result_layer.id"))
    result_layer = relationship("ResultLayer", back_populates = "measurements", cascade="all, delete-orphan", single_parent=True)

    image_id = Column(Integer, ForeignKey("image.id"))
    image = relationship("Image", back_populates = "measurements", cascade="all, delete-orphan", single_parent=True)

    # Many to Many
    experiment_groups = relationship(
        "ExperimentGroup",
        secondary= experiment_groups_measurements_association_table,
        back_populates = "measurements"
    )

class ExperimentGroup(Base):
    __tablename__ = "experiment_group"

    id = Column(Integer, primary_key=True, index = True)
    name = Column(String, nullable = False)
    hint = Column(String)
    description = Column(String)

    # One to One
    experiment_result = relationship("ExperimentResult", uselist = False, back_populates = "experiment_group")

    # Many to One
    experiment_id = Column(Integer, ForeignKey("experiment.id"))
    experiment = relationship("Experiment", back_populates = "experiment_groups", cascade="all, delete-orphan", single_parent=True)

    # Many to Many
    images = relationship(
        "Image",
        secondary= experiment_groups_images_association_table,
        back_populates = "experiment_groups"
    )

    result_layers = relationship(
        "ResultLayer",
        secondary= experiment_groups_result_layers_association_table,
        back_populates = "experiment_groups"
    )

    measurements = relationship(
        "Measurement",
        secondary = experiment_groups_measurements_association_table,
        back_populates = "experiment_groups"
    )

class ExperimentResult(Base):
    __tablename__ = "experiment_result"

    id = Column(Integer, primary_key=True, index = True)
    name = Column(String)
    description = Column(String)
    hint = Column(String)
    path = Column(String)
    result_type = Column(String)

    # One to One
    experiment_group_id = Column(Integer, ForeignKey("experiment_group.id"))
    experiment_group = relationship("ExperimentGroup", back_populates = "experiment_result")

class Experiment(Base):
    __tablename__ = "experiment"

    id = Column(Integer, primary_key=True, index = True)
    name = Column(String)
    hint = Column(String)
    description = Column(String)
    tags = Column(PickleType)

    # One to Many
    experiment_groups = relationship("ExperimentGroup", back_populates = "experiment")

class Classifier(Base):
    __tablename__ = "classifier"

    id= Column(Integer, primary_key=True, index = True)
    name= Column(String)
    clf_type= Column(PickleType)
    path_clf= Column(String)
    path_test_train= Column(String)
    params= Column(PickleType)
    metrics= Column(PickleType)
    tags= Column(PickleType)
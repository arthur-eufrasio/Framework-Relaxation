# -*- coding: utf-8 -*-
from abaqus import *
from abaqusConstants import *
from part import *
from step import *
from material import *
from section import *
from assembly import *
from interaction import *
from mesh import *

class RenameModel():
    
    def __init__(self, data_model):
        self.dataInput(data_model)

        mdb.Model(modelType=STANDARD_EXPLICIT, name=self.ModelName)
        del mdb.models["Model-1"]

    def dataInput(self, data_model):
        self.ModelName = str(data_model['generalInformation']['modelName'])

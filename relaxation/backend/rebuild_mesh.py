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
import math
import numpy as np


class RebuildMesh():

    def __init__(self, data_model, data_mesh):
        self.dataInput(data_model, data_mesh)
        self.createPart()
        self.createSetsandSections()
        self.setElemType()

    def dataInput(self, data_model, data_mesh):
        self.ModelName = str(data_model['generalInformation']['modelName'])
        self.PartName = str(data_model['partData']['createPartInformation']['Name'])
        self.odbOrtCutName = str(data_model['generalInformation']['odbOrtCutName'])

        self.NodesInfo = data_mesh[self.odbOrtCutName]['nodes']
        self.EleInfo = data_mesh[self.odbOrtCutName]['elements']

        self.m = mdb.models[self.ModelName]
    
    def createPart(self):
        self.p = self.m.Part(name=self.PartName, dimensionality=TWO_D_PLANAR, type=DEFORMABLE_BODY)

        node_dict = {}
        for nid, val in self.NodesInfo.items():
            x = float(val['coords'][0])
            y = float(val['coords'][2])
            coords = (x, y, 0.0)
            label = int(nid) 
            
            obj = self.p.Node(coordinates=coords, label=label)
            node_dict[nid] = obj

        for eid, val in self.EleInfo.items():
            connect = [str(n) for n in val['connectivity']]
            node_objs = (node_dict[connect[0]], node_dict[connect[1]],
                         node_dict[connect[2]], node_dict[connect[3]])

            self.p.Element(nodes=node_objs, elemShape=QUAD4, label=int(eid))

    def createSetsandSections(self):
        self.p.Set(elements= self.p.elements[:], name='allElements'+self.PartName)
        
        self.m.HomogeneousSolidSection(material='DA718', 
            name='Sec_DA718', thickness=None)
        self.p.SectionAssignment(offset=0.0, 
            offsetField='', offsetType=MIDDLE_SURFACE, region=
            self.p.sets['allElements'+self.PartName], 
            sectionName='Sec_DA718', thicknessAssignment=FROM_SECTION)
    
    def setElemType(self):
        self.p.setElementType(elemTypes=(
            ElemType(elemCode=CPE4RT, elemLibrary=STANDARD), ), regions= self.p.sets['allElements'+self.PartName])
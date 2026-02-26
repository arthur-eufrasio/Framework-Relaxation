# -*- coding: utf-8 -*-
import os
from abaqus import *
from abaqusConstants import *
from part import *
from step import *
from material import *
from section import *
from assembly import *
from interaction import *
from mesh import *
from visualization import *
from connectorBehavior import *


class AssemblyModel():
    def __init__(self, data_model, data_mesh):
        self.dataInput(data_model, data_mesh)
        self.assemblyPositions()
        self.stepsAndHistory()
        self.setFilmCondition()
        self.setBoundaryConditionsAndPredefinedFields()
        self.inpCreation()

    def dataInput(self, data_model, data_mesh):
        self.modelName = str(data_model['generalInformation']['modelName'])
        self.PartName = str(data_model['partData']['createPartInformation']['Name'])
        self.TimePeriod = data_model['assemblyAndSimulationData']['stepsAndHistoryInformation']['timePeriod']
        self.Dimensions = data_model['partData']['createPartInformation']['Dimensions']
        self.xPoints = sorted([self.Dimensions['x1'], self.Dimensions['x2']])
        self.yPoints = sorted([self.Dimensions['z1'], self.Dimensions['z2']])
        self.convCoef = data_model['assemblyAndSimulationData']['convBC']['convCoef']
        self.sinkTemp = data_model['assemblyAndSimulationData']['convBC']['sinkTemp']
        self.eleSize = data_model['partData']['createPartInformation']['eleSize']
        self.odbOrtCutName = str(data_model['generalInformation']['odbOrtCutName'])
        self.NodesInfo = data_mesh[self.odbOrtCutName]['nodes']

        self.m = mdb.models[self.modelName]

    def assemblyPositions(self):
        self.m.rootAssembly.DatumCsysByDefault(CARTESIAN)
        self.eulerianInst = self.m.rootAssembly.Instance(dependent=ON, name= self.PartName + '-1', part=self.m.parts[self.PartName])

    def stepsAndHistory(self):
        self.m.CoupledTempDisplacementStep(
            deltmx=20.0, name='RelaxationStep', previous='Initial', 
            timePeriod=self.TimePeriod, initialInc=1e-5, maxNumInc=1000, minInc=1e-6)

    def setFilmCondition(self):
        xMin = self.xPoints[0] - self.eleSize
        xMax = self.xPoints[1] + self.eleSize
        yMin = self.yPoints[1] - self.eleSize * 1.5
        yMax = self.yPoints[1] + self.eleSize * 0.5
        zMin = -self.eleSize
        zMax = +self.eleSize

        top_elements = self.eulerianInst.elements.getByBoundingBox(
            xMin= xMin, xMax= xMax,
            zMin= zMin, zMax= zMax,
            yMin= yMin, yMax= yMax
            )
        self.m.rootAssembly.Surface(face3Elements= top_elements, name='topElements'+self.PartName)
        topNodesSet = self.m.rootAssembly.Set(name='topNodesSet', nodes= self.m.rootAssembly.surfaces['topElementsZOI'].nodes)

        self.m.FilmCondition(createStepName='RelaxationStep', 
            definition=EMBEDDED_COEFF, filmCoeff=self.convCoef, filmCoeffAmplitude='', name=
            'naturalConvection', sinkAmplitude='', sinkDistributionType=UNIFORM, 
            sinkFieldName='', sinkTemperature=self.sinkTemp, surface=
            self.m.rootAssembly.surfaces['topElements'+self.PartName])
        
    def setBoundaryConditionsAndPredefinedFields(self):
        xMin = self.xPoints[1] - self.eleSize * 1.5
        xMax = self.xPoints[1] + self.eleSize * 0.5
        yMin = self.yPoints[0] - self.eleSize 
        yMax = self.yPoints[1] + self.eleSize
        zMin = -self.eleSize
        zMax = +self.eleSize

        right_elements = self.eulerianInst.elements.getByBoundingBox(
            xMin= xMin, xMax= xMax,
            zMin= zMin, zMax= zMax,
            yMin= yMin, yMax= yMax
            )
        self.m.rootAssembly.Surface(face2Elements= right_elements, name='rightElements'+self.PartName)
        rightNodesSet = self.m.rootAssembly.Set(name='rightNodesSet', nodes= self.m.rootAssembly.surfaces['rightElements'+self.PartName].nodes)

        xMin = self.xPoints[0] - self.eleSize * 0.5
        xMax = self.xPoints[0] + self.eleSize * 1.5
        yMin = self.yPoints[0] - self.eleSize 
        yMax = self.yPoints[1] + self.eleSize
        zMin = -self.eleSize
        zMax = +self.eleSize

        left_elements = self.eulerianInst.elements.getByBoundingBox(
            xMin= xMin, xMax= xMax,
            zMin= zMin, zMax= zMax,
            yMin= yMin, yMax= yMax
            )
        self.m.rootAssembly.Surface(face4Elements= left_elements, name='leftElements'+self.PartName)
        leftNodesSet = self.m.rootAssembly.Set(name='leftNodesSet', nodes= self.m.rootAssembly.surfaces['leftElements'+self.PartName].nodes)
        
        all_y_coords = []

        for node_obj in leftNodesSet.nodes:
            node_y_pos = node_obj.coordinates[1]
            all_y_coords.append(node_y_pos)

        all_y_coords.sort()
        
        xMin = self.xPoints[0] - self.eleSize * 0.5
        xMax = self.xPoints[1] + self.eleSize * 0.5
        yMin = self.yPoints[0] - self.eleSize 
        yMax = self.yPoints[0] + all_y_coords[1] + (all_y_coords[2] - all_y_coords[1]) / 2.0
        zMin = -self.eleSize
        zMax = +self.eleSize

        bottom_elements = self.eulerianInst.elements.getByBoundingBox(
            xMin= xMin, xMax= xMax,
            zMin= zMin, zMax= zMax,
            yMin= yMin, yMax= yMax
            )
        self.m.rootAssembly.Surface(face1Elements= bottom_elements, name='bottomElements'+self.PartName)
        bottomNodesSet = self.m.rootAssembly.Set(name='bottomNodesSet', nodes= self.m.rootAssembly.surfaces['bottomElements'+self.PartName].nodes)

        allNodesSet =self.m.rootAssembly.Set(name='allNodesSet', 
                                nodes= self.eulerianInst.nodes.getByBoundingBox(
                                xMin= self.xPoints[0] - self.eleSize, xMax= self.xPoints[1] + self.eleSize,
                                zMin= - self.eleSize, zMax= + self.eleSize,
                                yMin= self.yPoints[0] - self.eleSize, yMax=self.yPoints[1] + self.eleSize 
                                ))

        # self.m.DisplacementBC(amplitude=UNSET, createStepName='Initial', distributionType=UNIFORM, 
        #     fieldName='', localCsys=None, name='leftBC', region= leftNodesSet, 
        #     u1=SET, u2=UNSET, ur3=UNSET
        #     )
        # self.m.DisplacementBC(amplitude=UNSET, createStepName='Initial', distributionType=UNIFORM, 
        #     fieldName='', localCsys=None, name='rightBC', region= rightNodesSet, 
        #     u1=SET, u2=UNSET, ur3=UNSET
        #     )
        self.m.DisplacementBC(amplitude=UNSET, createStepName='Initial', distributionType=UNIFORM, 
            fieldName='', localCsys=None, name='bottomBC', region= bottomNodesSet, 
            u1=SET, u2=SET, ur3=UNSET
            )
        
        di = self.NodesInfo
        tempField = tuple((di[str(nid)]['coords'][0], di[str(nid)]['coords'][2], 0.0, di[str(nid)]['NT11']) for nid in di.keys())
        
        self.m.MappedField(description='', fieldDataType=
            SCALAR, localCsys=None, name='mapTempField', partLevelData=False, 
            pointDataFormat=XYZ, regionType=POINT, xyzPointData= tempField)
        self.m.Temperature(createStepName='Initial', 
            crossSectionDistribution=CONSTANT_THROUGH_THICKNESS, distributionType=FIELD
            , field='mapTempField', magnitudes=(1.0, ), name='initialTemperature', 
            region= allNodesSet)


    def inpCreation(self):
        job = mdb.Job(atTime=None, contactPrint=OFF, description='', echoPrint=OFF, 
            explicitPrecision=SINGLE, getMemoryFromAnalysis=True, historyPrint=OFF, 
            memory=90, memoryUnits=PERCENTAGE, model=self.modelName, modelPrint=
            OFF, multiprocessingMode=DEFAULT, name=self.modelName, 
            nodalOutputPrecision=SINGLE, numCpus=12, numDomains=12, numGPUs=0, 
            numThreadsPerMpiProcess=1, queue=None, resultsFormat=ODB, scratch='', type=
            ANALYSIS, userSubroutine='', waitHours=0, waitMinutes=0)
        
        backend_path = os.getenv("BACKEND_PROJECT_PATH", None)
        inp_folder_path = os.path.join(backend_path, 'files', 'inp')
        
        os.chdir(inp_folder_path)
        job.writeInput(consistencyChecking=OFF)

        os.chdir(backend_path)


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


class CreateMaterial():

    def __init__(self, data_model):
        self.dataInput(data_model)
        self.createMaterial()

    def dataInput(self, data_model):
        self.ModelName = str(data_model['generalInformation']['modelName'])
        self.PartName = str(data_model['partData']['createPartInformation']['Name'])
        self.materialInformation = data_model['partData']['materialInformation']

        self.m = mdb.models[self.ModelName]
        
    def createMaterial(self):
            self.m.Material(name='DA718')
            mat_i = self.materialInformation
            material_ref = self.m.materials['DA718']

            material_ref.Density(
                table=((mat_i['Density'],),)
            )

            material_ref.Elastic(
                table=tuple(
                    (ele['youngs_modulus'], ele['poissons_ratio'], ele['temp'])
                    for ele in mat_i['Elastic']
                ),
                temperatureDependency=ON
            )

            material_ref.Plastic(
                hardening=JOHNSON_COOK,
                table=((
                    mat_i['Plastic']['A'],
                    mat_i['Plastic']['B'],
                    mat_i['Plastic']['n'],
                    mat_i['Plastic']['m'],
                    mat_i['Plastic']['melting_temp'],
                    mat_i['Plastic']['ref_temp']
                ),)
            )

            material_ref.plastic.RateDependent(
                type=JOHNSON_COOK,
                table=((
                    mat_i['RateDependent']['C'],
                    mat_i['RateDependent']['epsilon_dot_0']
                ),)
            )

            material_ref.SpecificHeat(
                table=tuple(
                    (ele['specific_heat'], ele['temp'])
                    for ele in mat_i['SpecificHeat']
                ),
                temperatureDependency=ON
            )

            material_ref.Conductivity(
                table=tuple(
                    (ele['conductivity'], ele['temp'])
                    for ele in mat_i['Conductivity']
                ),
                temperatureDependency=ON
            )
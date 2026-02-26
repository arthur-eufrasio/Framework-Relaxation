# -*- coding: utf-8 -*-
from odbAccess import openOdb
from abaqusConstants import *
from abaqus import session
import math
import visualization
import json
import os


class DataExtractor:
    def __init__(self, config_odb, backend_project_path, path_dir_config):
        self.config_odb = config_odb

        self.backend_project_path = backend_project_path
        self.path_dir_config = path_dir_config

        self.odb = None
        self.odb_name = None
        self.odb_config = None
        self.data = {}
        self.path_name = None

        for odb_name, odb_config in self.config_odb.items():
            self.odb_name = str(odb_name)
            self.odb_config = odb_config

            DataExtractor.log("[Extractor] Extraction of the following ODB: {}".format(self.odb_name))

            self.ODB_PATH = str(self.odb_config['odb_path'])

            self.open_odb()
            self.get_parameters()
            self.data[self.odb_name] = {}
            self.data[self.odb_name]['elements'] = {}
            self.data[self.odb_name]['nodes'] = {}

            self.filter_nodes()
            DataExtractor.log("  [Extraction] Nodes had been filtered")
            self.filter_elements()
            DataExtractor.log("  [Extraction] Elements had been filtered")
            self.extract_equivalent_plastic_strain()
            DataExtractor.log("  [Extraction] Equivalent plastic strain had been extracted")
            self.extract_plastic_strain()
            DataExtractor.log("  [Extraction] Plastic strain had been extracted")
            self.extract_stress()
            DataExtractor.log("  [Extraction] Stresses had been extracted")
            self.extract_temperature()
            DataExtractor.log("  [Extraction] Temperatures had been extracted")

        self.process_path_data()

    @staticmethod
    def log(msg):
        log_path = "log/abaqus_log.txt"
        with open(log_path, "a") as f:
            f.write(msg + "\n")
            f.flush()

    def open_odb(self):
        DataExtractor.log("  [Extraction] Opening ODB: {}".format(self.ODB_PATH))
        self.odb = openOdb(path=self.ODB_PATH)

    def get_parameters(self):
        self.step_int = self.odb_config["step_index"]
        self.step_name = str(self.odb_config["step_name"])
        self.frame_target = self.odb_config["frame_target"]
        self.instance_name = str(self.odb_config["instance_name"])
        self.node_set_name = str(self.odb_config["node_set_name"])
        self.tolerance = self.odb_config["zoi_coordinates"]["tolerance"]

        self.zoi_coordinates = self.odb_config["zoi_coordinates"]

    def filter_nodes(self):
        self.instance = self.odb.rootAssembly.instances[self.instance_name]
        zoi = self.zoi_coordinates
        tolerance = self.tolerance
        valid_labels = []

        x_values = sorted([zoi['x1'], zoi['x2']])
        y_values = sorted([zoi['y1'], zoi['y2']])
        z_values = sorted([zoi['z1'], zoi['z2']])

        min_x = x_values[0] - tolerance
        max_x = x_values[1] + tolerance
        min_y = y_values[0] - tolerance
        max_y = y_values[1] + tolerance
        min_z = z_values[0] - tolerance
        max_z = z_values[1] + tolerance

        for node in self.instance.nodes:
            coords = node.coordinates
            if (min_x <= coords[0] <= max_x and
                    min_y <= coords[1] <= max_y and
                    min_z <= coords[2] <= max_z):
                valid_labels.append(node.label)
                self.data[self.odb_name]['nodes'][str(node.label)] = {}
                self.data[self.odb_name]['nodes'][str(node.label)]['coords'] = tuple(float(x) for x in coords)

        self.zoi_nodeLabels = tuple(valid_labels)

    def filter_elements(self):
        valid_nodes_set = set(self.zoi_nodeLabels)
        valid_elements = []

        for element in self.instance.elements:
            valid_element_nodes = [
                node for node in element.connectivity if node in valid_nodes_set
            ]

            if len(valid_element_nodes) >= 4:
                valid_elements.append(element.label)
                
                str_label = str(element.label)
                connectivity_ordered = self._order_connectivity(valid_element_nodes, self.data[self.odb_name]['nodes'])
                self.data[self.odb_name]['elements'][str_label] = {}
                self.data[self.odb_name]['elements'][str_label]['connectivity'] = connectivity_ordered

        valid_elements = tuple(valid_elements)
        self.zoi_elementLabels = set(valid_elements)

    def extract_equivalent_plastic_strain(self):
        step = self.odb.steps[self.step_name]
        frame = step.frames[self.frame_target]
        field_name = 'PEEQ_ASSEMBLY_EULERIAN-1_DA718_PENG20-1'
        fdo = frame.fieldOutputs[field_name]

        for value in fdo.values:
            if value.elementLabel in self.zoi_elementLabels:
                str_label = str(value.elementLabel)
                data_value = float(value.data)

                self.data[self.odb_name]['elements'][str_label]['PEEQ'] = data_value

    def extract_plastic_strain(self):
        step = self.odb.steps[self.step_name]
        frame = step.frames[self.frame_target]
        field_name = 'PE_ASSEMBLY_EULERIAN-1_DA718_PENG20-1'
        fdo = frame.fieldOutputs[field_name]

        for value in fdo.values:
            if value.elementLabel in self.zoi_elementLabels:
                str_label = str(value.elementLabel)
                data_tuple = tuple(float(x) for x in value.data)

                self.data[self.odb_name]['elements'][str_label]['PE'] = data_tuple

    def extract_stress(self):
        step = self.odb.steps[self.step_name]
        frame = step.frames[self.frame_target]
        fdo = frame.fieldOutputs['S_ASSEMBLY_EULERIAN-1_DA718_PENG20-1']

        for value in fdo.values:
            if value.elementLabel in self.zoi_elementLabels:
                str_label = str(value.elementLabel)
                data_tuple = tuple(float(x) for x in value.data)

                self.data[self.odb_name]['elements'][str_label]['S'] = data_tuple

    def extract_temperature(self):
        step = self.odb.steps[self.step_name]
        frame = step.frames[self.frame_target]
        node_set = self.instance.elementSets[self.node_set_name]
        fdo = frame.fieldOutputs['NT11'].getSubset(region=node_set)

        for value in fdo.values:
            if value.nodeLabel in self.zoi_nodeLabels and value.instance.name == self.instance_name:
                str_label = str(value.nodeLabel)
                data_value = float(value.data)
                self.data[self.odb_name]['nodes'][str_label]['NT11'] = data_value

    def _order_connectivity(self, valid_element_nodes, node_coords_data):
        connectivity_data = []
        for node_id in valid_element_nodes:
            connectivity_data.append({
                'nid': node_id,
                'coord': node_coords_data[str(node_id)]['coords']
            })

        x_sum = sum(d['coord'][0] for d in connectivity_data)
        z_sum = sum(d['coord'][2] for d in connectivity_data)
        centroid = (x_sum / 4.0, z_sum / 4.0)

        connectivity_data.sort(key=lambda node: math.atan2(
            node['coord'][2] - centroid[1],
            node['coord'][0] - centroid[0]
        ))

        return [d['nid'] for d in connectivity_data]

    def process_path_data(self):
            DataExtractor.log("[Extractor] Saving all extracted data to JSON file...")

            output_file_name = "data.json"
            output_json_path = os.path.join(self.path_dir_config, output_file_name)

            with open(output_json_path, "w") as f:
                json.dump(self.data, f, indent=4)

            DataExtractor.log("  [Extraction] File saved to: {}".format(output_json_path))

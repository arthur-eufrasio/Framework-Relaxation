# -*- coding: utf-8 -*-
import sys
import os
import json

os.chdir(os.getenv("BACKEND_PROJECT_PATH", None))
sys.dont_write_bytecode = True

from rebuild_mesh import RebuildMesh
from rename_model import RenameModel
from create_material import CreateMaterial
from assembly_and_simulation import AssemblyModel

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


class Command:
    def __init__(self):
        log_path = "log/abaqus_log.txt"
        if os.path.exists(log_path):
            os.remove(log_path)

    @staticmethod
    def log(msg):
        log_dir = "log"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        log_path = os.path.join(log_dir, "abaqus_log.txt")
        with open(log_path, "a") as f:
            f.write(msg + "\n")
            f.flush()

    def create_paths(self):
        self.backend_project_path = os.getenv("BACKEND_PROJECT_PATH", None)
        self.framework_project_path = os.path.dirname(os.path.dirname(self.backend_project_path))

        self.path_dir_config = os.path.join(
            self.framework_project_path, "config"
        )

        Command.log("[Command] The paths to the directories were successfully created.")
        Command.log("       - Extraction Dir Config Path: " + self.path_dir_config)

    def read_model_config(self):
        path_model_config = os.path.join(
            self.path_dir_config, "model_config.json"
        )

        with open(path_model_config, 'r') as file:
            model_config = json.load(file)

        return model_config

    def read_nodes_ele_data(self):
        path_nodes_ele_data = os.path.join(
            self.path_dir_config, "data.json"
        )

        with open(path_nodes_ele_data, 'r') as file:
            nodes_ele_data = json.load(file)

        return nodes_ele_data


    def run_command(self):
        Command.log("[Command] Start model creation...\n")

        Command.log("   [Command] Creating path.\n")
        self.create_paths()

        Command.log("   [Command] Reading required data.\n")
        data_model = self.read_model_config()
        data_nodes_ele = self.read_nodes_ele_data()

        Command.log("       [Command] Renaming model.\n")
        RenameModel(data_model)

        Command.log("       [Command] Creating Material.\n")
        CreateMaterial(data_model)

        Command.log("       [Command] Rebuilding mesh.\n")
        RebuildMesh(data_model, data_nodes_ele)

        Command.log("       [Command] Creating Assembly.\n")
        AssemblyModel(data_model, data_nodes_ele)

        Command.log("[Command] End.")


if __name__ == "__main__":
    try:
        command = Command()
        command.run_command()

    except Exception as e:
        import traceback
        
        log_dir = "log"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        log_path = os.path.join(log_dir, "abaqus_log.txt")

        with open(log_path, "a") as f:
            f.write("\n====================================================\n")
            f.write("\n[COMMAND ERROR] An exception occurred during execution:\n")
            traceback.print_exc(file=f)
            f.write("\n====================================================\n")


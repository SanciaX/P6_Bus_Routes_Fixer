import os
import json
from pathlib import Path
import logging
import shutil



class DirectoryConfig:
    _instance = None
    DEFAULT_CONFIG_PATH = "bus_routes_fixer/config/directories_P6_Example.json"
    WORKING_DIRECTORY = os.getcwd()

    def __new__(cls, config_path="bus_routes_fixer/config/directories_P6_Example.json"):
        if cls._instance is None:
            cls._instance = super(DirectoryConfig, cls).__new__(cls)
            cls._instance._initialize(config_path)
        return cls._instance

    def _initialize(self, config_path=None):
        # Get the current working directory
        current_path = Path(self.WORKING_DIRECTORY)
        logging.info(f"The current working directory is: {current_path}")

        if not config_path:
            config_path = self.DEFAULT_CONFIG_PATH
        # Construct the path to the directories.json file
        self.json_path_path = current_path / config_path
        logging.info(f"The JSON file path is: {self.json_path_path}")

        # Check if the file exists
        if not self.json_path_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.json_path_path}")

        # Load the JSON file
        with open(self.json_path_path, 'r') as file:
            directories = json.load(file)

        # Visum version
        self.visum_version = directories["visum_version"]

        # Assign base paths
        self.bus_routes_fix_path = current_path / directories["base_path"]
        self.scenario_management_base_path = Path(directories["scenario_management_base_path"])
        self.scenario_management_project_path = Path(directories["scenario_management_project_path"])
        self.modifications_path = Path(self.scenario_management_base_path) / "Modifications"
        self.scenarios_path = Path(self.scenario_management_base_path) / "Scenarios"

        # Clear files in the screenshots folder if it exists
        self.screenshots_path = current_path / 'bus_routes_fixer/outputs/bus_routes_screenshots'
        if os.path.exists(self.screenshots_path):
            for filename in os.listdir(self.screenshots_path):
                file_path = os.path.join(self.screenshots_path, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.remove(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    logging.error(f'Failed to delete {file_path}. Reason: {e}')
        else:
            logging.info(f'The path {self.screenshots_path} does not exist.')
            
        # screenshot gpas' paths
        self.gpa_path = current_path / 'bus_routes_fixer/resources/bus_route_fixer.gpa'
        self.prior_error_gpa_path = current_path / 'bus_routes_fixer/resources/prior_error.gpa'
        self.after_fixing_gpa_path = current_path / 'bus_routes_fixer/resources/after_fixing.gpa'
        self.error_modification_gpa_path = current_path / 'bus_routes_fixer/resources/error_modification.gpa'

        #Clear files in the bus_routes_fix_path if it exists
        if os.path.exists(self.bus_routes_fix_path):
            for filename in os.listdir(self.bus_routes_fix_path):
                file_path = os.path.join(self.bus_routes_fix_path, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.remove(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    logging.error(f'Failed to delete {file_path}. Reason: {e}')

        # Create the base path if it does not exist
        Path(self.bus_routes_fix_path).mkdir(exist_ok=True, parents=True)

        # Assign IDs
        self.error_scenario_id = directories["error_scenario_id"]
        self.first_error_modification_id_str = directories["id_of_the_1st_error_modification"]
        self.first_error_modification_id = str(int(self.first_error_modification_id_str.strip())).zfill(6)

        # Define specific files using relative paths
        self.scenario_management_path = self.scenario_management_base_path / '00_Bus_Routes_Fixer_Test_P6_Model.vpdbx'
        self.error_scenario_id_str = f"S{str(self.error_scenario_id).zfill(6)}"
        self.error_message_path = self.scenarios_path / self.error_scenario_id_str
        self.error_message_path = self.error_message_path / 'Messages.txt'
        self.error_message_log = self.bus_routes_fix_path / 'MessageLog.txt'
        self.working_scenario_path = self.bus_routes_fix_path / 'scenarioWorking.ver'
        self.error_scenario_fixing_routes_path = self.bus_routes_fix_path / 'scenarioErrorFixing.ver'
        self.working_scenario_delete_routes_path = self.bus_routes_fix_path / 'scenarioWorkingDeleteRoutes.ver'
        self.route_deleted_transfer_path = self.bus_routes_fix_path / 'routeDeletedTransfer.tra'
        self.route_fixed_transfer_path = self.bus_routes_fix_path / 'fixedRouteAddedTransfer.tra'
        self.debug_log_path = self.bus_routes_fix_path / 'debug.log'
        self.derived_data_log_path = self.bus_routes_fix_path / 'Notes_for_Visum_Modeller.log'
        self.list_of_modification_since_the_1st_error_paths = []
        self.list_of_scenarios_built_when_adding_each_error_modification = []
        self.list_fixed_error_modification_paths = []
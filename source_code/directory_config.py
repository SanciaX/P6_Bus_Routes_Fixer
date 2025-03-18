import os
import json
from pathlib import Path
import logging


class DirectoryConfig:
    _instance = None  # Singleton pattern to ensure only one instance is created
    DEFAULT_CONFIG_PATH = "config/directories.json"
    WORKING_DIRECTORY = os.getcwd()

    def __new__(cls, config_path="config/directories.json"):
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
        self.modifications_path = Path(
            self.scenario_management_base_path) / "Modifications"
        self.scenarios_path = Path(
            self.scenario_management_base_path) / "Scenarios"

        # Create the base path if it does not exist
        Path(self.bus_routes_fix_path).mkdir(exist_ok=True, parents=True)

        # Assign IDs
        self.error_scenario_id = directories["error_scenario_id"]
        self.error_modification_id = directories["error_modification_id"]

        # Define specific files using relative paths
        self.scenario_management_path = self.scenario_management_base_path / 'Bus_Route_Script_Test_Subnetwork.vpdbx'
        self.error_modification = self._get_error_modification_path()
        self.error_scenario_id_str = f"S{str(self.error_scenario_id).zfill(6)}"
        self.error_message_path = self.scenarios_path / self.error_scenario_id_str
        self.error_message_path = self.error_message_path / 'Messages.txt'
        self.error_message_log = self.bus_routes_fix_path / 'MessageLog.txt'

        self.working_scenario_path = self.bus_routes_fix_path / 'scenarioWorking.ver'
        self.error_scenario_path = self.bus_routes_fix_path / 'scenarioError.ver'
        self.error_scenario_fixing_routes_path = self.bus_routes_fix_path / 'scenarioErrorFixing.ver'
        self.working_scenario_delete_routes_path = self.bus_routes_fix_path / 'scenarioWorkingDeleteRoutes.ver'
        self.route_deleted_transfer_path = self.bus_routes_fix_path / 'routeDeletedTransfer.tra'
        self.route_fixed_transfer_path = self.bus_routes_fix_path / 'fixedRouteAddedTransfer.tra'
        self.fixed_error_modification_path = self.bus_routes_fix_path / 'fixedErrorModificationFile.tra'
        self.debug_log_path = self.bus_routes_fix_path / 'debug.log'
        self.derived_data_log_path = self.bus_routes_fix_path / 'Notes_for_Visum_Modeller.log'

    def _get_error_modification_path(self):
        """
        Generate the error modification file path dynamically.
        """
        base_mod_path = str(self.modifications_path / 'M000000.tra')
        mod_path_list = list(base_mod_path)
        mod_id_length = len(str(self.error_modification_id))
        mod_path_list[-mod_id_length - 4: -4] = str(self.error_modification_id)
        return ''.join(mod_path_list)

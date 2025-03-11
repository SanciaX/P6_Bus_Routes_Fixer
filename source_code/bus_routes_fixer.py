"""
# -*- coding: utf-8 -*-
This version addresses various route error types through shortest-path search including 'turn closed', 'no link', ''is blocked for the transport system''
Author: Shanshan Xie, Adam Fradgley, Birendra Shrestha
Adapted from: P6FixBusRoute30.py (Birendra Shrestha)

Instructions:
- Step 1: Specify 'scenario_management_base_path', 'scenario_management_project_path' 'error_modification_id' & 'error_scenario_id' in the ../directories.json
- Step 2: Run the main script 'bus_routes_fixer.py'
"""

import logging
import os
import win32com.client

###### PREPARATIONS:
# Import User's Inputs
from directory_config import config
from fix_routes_functions import find_error_links, add_routes_back
from save_to_sm import save_to_sm
from logger_configuration import setup_logger
from identify_error_functions import read_scenario_management, save_error_routes, save_fixed_error_modification, save_the_routes_deleting_ver



class VisumConnector:
    """Manages connections to PTV Visum."""

    def __init__(self, visum_version):
        self.visum_version = visum_version
        self.visum = None

    def connect(self):
        """Connects to Visum."""
        try:
            self.visum = win32com.client.gencache.EnsureDispatch(f"Visum.Visum.{self.visum_version}")
            logging.info(f"PTV Visum started: {self.visum}")
            return self.visum
        except Exception as e:
            logging.error(f"Error connecting to Visum: {e}")
            raise

    def close(self):
        """Closes the Visum connection."""
        if self.visum:
            self.visum = None
            logging.info("Visum connection closed.")


class BusRoutesFixer:
    """Main class to fix bus route errors in Visum."""
    DEFAULT_CONFIG_PATH = "../config/directories.json"
    WORKING_DIRECTORY = os.getcwd()
    BUS_ROUTES_FIXING_DIRECTORY = os.path.join(WORKING_DIRECTORY, "bus_route_fixing_temp")

    def __init__(self, config_path=None):
        """Initializes the BusRoutesFixer with configuration and Visum connections."""
        if not config_path:
            config_path = self.DEFAULT_CONFIG_PATH
        self.config = config
        self.logger = setup_logger()
        self.visum_connector1 = VisumConnector(self.config.visum_version)
        self.visum1 = self.visum_connector1.connect()  # visum1 is linked to the scenario management project
        self.sm_project = self.visum1.ScenarioManagement.OpenProject(self.config.scenario_management_path)
        self.com_constants = win32com.client.constants
        self.error_routes_dict = None
        self.node_chains = None

    def run_fixer(self):
        try:
            self._identify_errors()
            self._fix_errors()
            self._save_to_sm()

        except Exception as e:
            self.logger.error(f"An error occurred during the fixing process: {e}", exc_info=True)
        finally:
            self.close()

    def _identify_errors(self):
        # Identify the modification causing errors and create a new scenario containing the modifications before the error occurs and save the workingscenario.ver file
        self.new_mode_set = read_scenario_management(self.visum1, self.sm_project, self.config)

        # Save route items along the error routes in the network before loading the error modification
        self.visum_connector2 = VisumConnector(self.config.visum_version)
        self.visum2 = self.visum_connector2.connect() # visum2 is linked to scenarioWorking.ver
        self.error_routes_dict = save_error_routes(self.visum1, self.visum2, self.config) # Note: visum1 is used to delete the error routes, visum2 is used to index error routes

        # Create fixedErrorModificationFile.tra, which is a copy of the error modification but with no info. about the error routes already deleted from the network.
        # This is to avoid errors that may occur when loading the error modification if the original error modification .tra contains data about error routes that are already deleted
        save_fixed_error_modification(self.visum1, self.config)

        # Save the transfer file that deletes routes from the working scenario (routeDeletedTransfer.tra) and apply it to a new modification in scenario management
        save_the_routes_deleting_ver(self.visum1, self.sm_project, self.config)

    def _fix_errors(self):
        self.visum_connector3 = VisumConnector(self.config.visum_version)
        self.visum3 = self.visum_connector3.connect() # visum3 is linked to scenarioError.ver

        # Use the network of the error scenario to find problematic link(s) along error route(s)
        self.error_routes_dict = find_error_links(self.error_routes_dict, self.visum1)

        # Generate the transfer file that adds the fixed routes back
        add_routes_back(self.error_routes_dict, self.visum3, self.config)


    def _save_to_sm(self):
        save_to_sm(self.sm_project, self.config, self.new_mode_set, self.visum1)

    def close(self):
        """Closes Visum connections."""
        if self.visum_connector1:
            self.visum_connector1.close()
        if self.visum_connector2:
            self.visum_connector2.close()
        if self.visum_connector3:
            self.visum_connector3.close()
        logging.info("Visum connections closed.")


def main(config_path=None):
    bfr = BusRoutesFixer(config_path)
    bfr.run_fixer()


if __name__ == "__main__":  # checks if the script is being run directly; This allows the script to be used both as a standalone program and as a module that can be imported without executing the main function.
    main()

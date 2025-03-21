

import logging
import os

from source_code.directory_config import DirectoryConfig
from source_code.scenario_management_helper import ScenarioManagementHelper
from source_code.logger_configuration import setup_logger
from source_code.visum_connection import VisumConnection

logger = setup_logger()


class BusRoutesFixer:
    """Main class to fix bus route errors in Visum."""
    DEFAULT_CONFIG_PATH = "config/directories.json"
    WORKING_DIRECTORY = os.getcwd()
    BUS_ROUTES_FIXING_DIRECTORY = os.path.join(WORKING_DIRECTORY, "bus_route_fixing_temp")

    def __init__(self, config_path=None):
        """Initializes the BusRoutesFixer with configuration and Visum connections."""
        if not config_path:
            config_path = self.DEFAULT_CONFIG_PATH
        self.config = DirectoryConfig(config_path) # Creates and loads the configuration
        self.scenario_management_project = ScenarioManagementHelper(self.config.scenario_management_path, self.config)

    def run_fixer(self):
        """Main function to identify and fix bus route errors."""
        logging.info("Starting bus route fixing process...")

        ###### IDENTIFY ERRORS:
        # Identify the modification causing errors and create a new scenario containing the modifications before the error occurs and save the workingscenario.ver file
        self.scenario_management_project.read_scenario_management(self.config)
        # Save route items along the error routes in the network before loading the error modification
        # Note: visum1 is used to delete the error routes, visum2 is used to index error routes
        self.scenario_management_project.save_error_routes()
        # Create fixedErrorModificationFile.tra, which is a copy of the error modification but with no info. about the error routes already deleted from the network.
        # This is to avoid errors that may occur when loading the error modification if the original error modification .tra contains data about error routes that are already deleted
        self.scenario_management_project.save_fixed_error_modification()

        # Save the transfer file that deletes routes from the working scenario (routeDeletedTransfer.tra) and apply it to a new modification in scenario management
        self.scenario_management_project.save_the_routes_deleting_ver()

        ###### FIX ERRORS
        # Use the network of the error scenario to find problematic link(s) along error route(s)
        self.scenario_management_project.find_error_links()

        # Generate the transfer file that adds the fixed routes back
        self.scenario_management_project.add_routes_back()

        ###### SAVE TO SCENARIO MANAGEMENT:
        self.scenario_management_project.save_to_scenario_manager(self.scenario_management_project.working_scenario_modification_list)

        # close the visum instances
        self.close()

    def close(self):
        """Closes Visum connections."""
        self.scenario_management_project.close()


def main(config_path=None):
    bfr = BusRoutesFixer(config_path)
    bfr.run_fixer()


if __name__ == "__main__":  # checks if the script is being run directly; This allows the script to be used both as a standalone program and as a module that can be imported without executing the main function.
    main()



import logging
import os

from bus_routes_fixer.directory_config import DirectoryConfig
from bus_routes_fixer.scenario_management_helper import ScenarioManagementHelper
from bus_routes_fixer.logger_configuration import setup_logger

logger = setup_logger()


class BusRoutesFixer:
    """Main class to fix bus route errors in Visum."""
    DEFAULT_CONFIG_PATH = "bus_routes_fixer/config/directories.json"
    WORKING_DIRECTORY = os.getcwd()
    BUS_ROUTES_FIXING_DIRECTORY = os.path.join(WORKING_DIRECTORY, "outputs")

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
        # Identify the modification causing errors; create a new scenario containing the modifications before the error occurs and save as workingscenario.ver
        logging.info("Starting reading scenario management.")
        self.scenario_management_project.read_scenario_management(self.config)
        # Save route items along the error routes in the network before loading the error modification
        # Note: visum_connection1 is used to delete the error routes and save the routes_deleting_ver as a new modification, visum_connection2 keeps these error routes so that we can get routes' and routeitems' attributes from its connection
        logging.info("Starting saving error route instance.")
        self.scenario_management_project.save_error_routes()

        # Create fixedXXXXXX.tra, which are copies of the modifications from the first modification causing route errors, but without data about the error routes already deleted from the network.
        # Using new copies of these modifications instead of the original ones aims to avoid errors that may occur when loading these modifications if any of the original modifications contains data about error routes that are already deleted
        logging.info("Starting saving fixed modifications.")
        self.scenario_management_project.save_fixed_modifications()

        # Save the transfer file that deletes routes from the working scenario (routeDeletedTransfer.tra) and use it as a new modification in scenario management
        self.scenario_management_project.save_the_routes_deleting_ver()

        ###### FIX ERRORS
        # Use the network of the error scenario to find problematic link(s)/turn(s) and route item(s) along error route(s)
        logging.info("Starting identifying problematic link(s)/turn(s) and route item(s).")
        self.scenario_management_project.find_stop_pairs_to_search_path()

        # Generate the transfer file that adds the fixed routes back
        logging.info("Starting adding routes back.")
        self.scenario_management_project.add_routes_back()

        # Take a screenshot of each error route in the error modification
        self.scenario_management_project.take_screenshots_in_modifications()

        ###### SAVE TO SCENARIO MANAGEMENT:
        logging.info("Starting creating the final scenario with fixed line routes.")
        self.scenario_management_project.save_to_scenario_manager(self.scenario_management_project.list_of_mods_pre_1st_error, self.scenario_management_project.list_of_mods_from_1st_error)

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

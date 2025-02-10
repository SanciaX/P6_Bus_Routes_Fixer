"""
# -*- coding: utf-8 -*-
This version addresses various route error types through shortest-path search including 'turn closed', 'no link', ''is blocked for the transport system''
Author: Shanshan Xie
Adapted from: P6FixBusRoute30.py (Birendra Shrestha)

Instructions:
- Step 1: Specify 'scenario_management_path', 'error_modification_id' & 'error_scenario_id' in the ../directories.json 
- Step 2: Run the main script 'bus_routes_fixer.py'
"""
import logging
import os
import shutil
from pathlib import Path

import win32com.client

from config_loader import ConfigLoader
from copy_files_from_scenario_management import copy_files_from_scenario_management
from error_node_stop_route_lists import ErrorNodeStopList, ErrorNodeList
from error_reading import ModificationCheckList
from get_node12ok_list import get_node12ok_list
from identify_error_routes import identify_errors
from message_errors import MessageErrors
from route_nodes import RouteNodes
from save_to_sm import save_to_sm
from show_n_save_messages import show_n_save_messages
from utility_functions import setup_logger
from visum_path_search import visum_path_search
from visum_pre_search_path import prepare_visum_transferfile

logger = setup_logger()


class BusRoutesFixer:
    DEFAULT_CONFIG_PATH = "config/directories.json"
    WORKING_DIRECTORY = os.getcwd()
    BUS_ROUTES_FIXING_DIRECTORY = os.path.join(WORKING_DIRECTORY, "bus_route_fixing_temp")

    def __init__(self, config_path=None):
        if not config_path:
            config_path = self.DEFAULT_CONFIG_PATH
        self.config = ConfigLoader.from_config_path(config_path)
        self.set_fixed_paths()
        self.create_directories()
        self.visum = win32com.client.gencache.EnsureDispatch(f"Visum.Visum.{self.config.visum_version}")
        logging.info(f"PTV Visum started: {self.visum}")
        self.com_constants = win32com.client.constants
        self.message_errors = MessageErrors()

    def run_fixer(self):
        self.scenario_management_project = self.visum.ScenarioManagement.OpenProject(
            self.config.scenario_management_project_path
        )
        self.prepare_scenarios()
        self.message_errors.get_errors_from_messages(self.visum.Messages)
        self.prepare_visum_transfer_file()

        # TODO reorganise the remaining steps below to integrate with the changes above

        (error_route_mojibake, error_dirs, error_directions, error_nodes_check, error_route_names, error_route,
         error_nodes_class, node_check_list_class, error_route_list_class, check_node_pair_ok_class,
         fix_bus_route_class, num_of_routes, error_routes, error_nodes_type_check) = identify_errors(
            self.error_message_file,
            self.network_file_table_of_links,
            self.network_file_table_of_turns)

        new_mod_delete_routes, mod_delete_routes_name, mod_delete_routes_file = prepare_visum_transferfile(
            self.visum, self.scenario_management_path, self.scenario_management_project, self.working_scenario_name,
            num_of_routes, error_routes,
            error_dirs,
            error_directions, self.working_scenario_delete_routes_name, self.route_added_transfer_file_start,
            self.route_deleted_transfer_file
        )

        modification_check, node_links, error_node_stop_list, num_of_node_stop, error_route_list_long, error_node_list1, error_route_list, num_of_nodes, = get_node12ok_list(
            error_route_mojibake, RouteNodes, ErrorNodeList, ErrorNodeStopList, ModificationCheckList,
            self.route_added_transfer_file_start, self.error_scenario_network_file_name,
            self.network_file_table_of_links,
            self.network_file_table_of_turns, self.error_modification_file, error_nodes_check, error_nodes_type_check,
            check_node_pair_ok_class
        )

        ## Create a new .ver for shortest path search (where problematic routes have been deleted)
        all_messages, search_chains, nodes_delete_list, error_mod_transfer_file, routes_fixed_transfer_file = visum_path_search(
            self.com_constants, self.working_scenario_delete_routes_name, self.error_modification_file,
            self.error_scenario_network_file_name, node_links,
            error_route_list, self.route_added_transfer_file_start, self.route_added_transfer_file_temp,
            fix_bus_route_class,
            self.route_added_transfer_file_final, modification_check, self.network_file_table_of_links,
            self.network_file_table_of_turns, check_node_pair_ok_class,
            self.processed_error_mod_transfer_file,
            self.working_scenario_load_error_mod,
            self.error_mod_transfer_file,
            self.working_scenario_routes_fixed_name,
            self.routes_fixed_transfer_file
        )

        ## copying final transfer files to mod files
        new_mod_no2, this_mod_name2, mod_file_name2, new_mod_no3, this_mod_name3, mod_file_name3, new_mod_set, cur_scenario_id, error_message_file_fixed = save_to_sm(
            self.scenario_management_project, self.scenario_management_path, self.processed_error_mod_transfer_file,
            self.route_added_transfer_file_final,
            self.old_mod_set, new_mod_delete_routes, self.error_message_path, self.visum
        )

    def prepare_visum_transfer_file(self):
        # Load the network before error occurs
        self.visum.LoadVersion(self.working_scenario_name)
        for error_message in self.message_errors.error_list:
            route_to_delete = self.visum.Net.LineRoutes.ItemByKey(
                error_message.line_name,
                error_message.line_route_direction,
                error_message.line_route_name
            )
            if route_to_delete:
                self.visum.Net.RemoveLineRoute(route_to_delete)

        # Create a transfer file of adding routes (reverse the deletion action))
        self.visum.GenerateModelTransferFileBetweenVersionFiles(
            self.working_scenario_delete_routes_name,
            self.working_scenario_name,
            self.route_added_transfer_file_start,
            LayoutFile="",
            NonDefaultOnly=False,
            NonEmptyTablesOnly=True,
            WriteLayoutIntoModelTransferFile=True,
        )
        # Create a transfer file of adding routes (the deletion action))
        self.visum.GenerateModelTransferFileBetweenVersionFiles(
            self.working_scenario_name,
            self.working_scenario_delete_routes_name,
            self.route_deleted_transfer_file,
            LayoutFile="",
            NonDefaultOnly=False,
            NonEmptyTablesOnly=True,
            WriteLayoutIntoModelTransferFile=True,
        )

        # Create a new modification to delete the routes
        new_modification1 = self.scenario_management_project.AddModification()
        new_modification1.SetAttValue("Code", "Erroneous Routes Deleted")
        new_modification1.SetAttValue(
            "Description", "Copied from the last working modification and have problematic routes deleted"
        )
        new_mod_delete_routes = int(new_modification1.AttValue("No"))
        mod_delete_routes_name = new_modification1.AttValue("TraFile")
        mod_delete_routes_file = os.path.join(self.config.scenario_management_base_path, "Modifications",
                                              mod_delete_routes_name)
        # copy the transfer file to the path of the scenario management's Modification folder
        shutil.copy2(self.route_deleted_transfer_file, mod_delete_routes_file)

    def set_fixed_paths(self):
        # Define base paths
        self.bus_routes_fix_path = Path(
            self.WORKING_DIRECTORY) / "route_fixing_folder"  # current_path / directories['base_path']
        self.scenario_management_path = self.config.scenario_management_base_path
        self.modifications_path = Path(
            self.scenario_management_path) / "Modifications"  # scenario_management_path / directories['modifications_path']
        self.scenarios_path = Path(
            self.scenario_management_path) / "Scenarios"  # scenario_management_path / directories['scenarios_path'
        self.error_modification_file = self.modifications_path / f"M{self.config.error_modification_id.zfill(6)}.tra"
        error_scenario_id_str = f"S{self.config.error_scenario_id.zfill(6)}"
        self.error_message_path = self.scenarios_path / error_scenario_id_str
        self.error_message_file = self.error_message_path / 'Messages.txt'
        self.error_message_log = self.bus_routes_fix_path / 'MessageLog.txt'
        self.working_scenario_name = self.bus_routes_fix_path / 'scenarioWorking.ver'
        self.working_scenario_delete_routes_name = self.bus_routes_fix_path / 'scenarioWorkingDeleteRoutes.ver'
        self.working_scenario_load_error_mod = self.bus_routes_fix_path / 'working_scenario_load_error_mod.ver'
        self.working_scenario_routes_fixed_name = self.bus_routes_fix_path / 'scenarioWorkingRoutesFixed.ver'
        self.route_search_version = self.bus_routes_fix_path / 'route_search_model.ver'
        self.error_scenario_network_file_name = self.bus_routes_fix_path / 'NetworkFileError.net'
        self.network_file_table_of_links = self.bus_routes_fix_path / 'NetworkFileErrorLinks.net'
        self.network_file_table_of_turns = self.bus_routes_fix_path / 'NetworkFileErrorTurns.net'
        self.route_deleted_transfer_file = self.bus_routes_fix_path / 'routeDeletedTransfer.tra'
        self.route_added_transfer_file_start = self.bus_routes_fix_path / 'routeAddedTransferStart.tra'
        self.route_added_transfer_file_temp = self.bus_routes_fix_path / 'routeAddedTransferTemp.tra'
        self.route_added_transfer_file_final = self.bus_routes_fix_path / 'routeAddedTransferFileFinal.tra'
        self.routes_fixed_transfer_file = self.bus_routes_fix_path / 'routeFixedTransferFile.tra'
        self.error_mod_transfer_file = self.bus_routes_fix_path / 'error_mod_transfer_file.tra'
        self.processed_error_mod_transfer_file = self.bus_routes_fix_path / 'processed_error_mod_transfer_file.tra'

    def prepare_scenarios(self):
        self.error_scenario = self.visum.ScenarioManagement.CurrentProject.Scenarios.ItemByKey(
            self.config.error_scenario_id)
        modification_id_list = self.error_scenario.AttValue("MODIFICATIONS").split(',')
        working_modification_id_str = ','.join(modification_id_list[:-1])
        working_scenario = self.scenario_management_project.AddScenario()  # Add a new scenario with all the modifications before the error occurs
        working_scenario_id = working_scenario.AttValue("NO")
        working_scenario.SetAttValue("CODE", "Deselect the modification causing error")
        working_scenario.SetAttValue("PARAMETERSET", "1")
        working_scenario.SetAttValue("MODIFICATIONS", working_modification_id_str)
        working_scenario_path = 'S000000'[:-len(str(int(working_scenario_id)))] + str(int(working_scenario_id))
        error_message_file_working = self.scenarios_path / working_scenario_path / 'Messages.txt'
        self.visum.SetErrorFile(error_message_file_working)
        working_scenario.LoadInput()
        self.visum.SaveVersion(self.working_scenario_name)

        self.error_scenario.LoadInput()
        self.visum.IO.SaveNet(
            self.error_scenario_network_file_name,
            LayoutFile="",
            EditableOnly=True,
            NonDefaultOnly=True,
            ActiveNetElemsOnly=False,
            NonEmptyTablesOnly=True,
        )
        self.visum.SetErrorFile(self.error_message_log)
        self.old_mod_set = self.error_scenario.AttValue("MODIFICATIONS")

    def create_directories(self):
        Path(self.BUS_ROUTES_FIXING_DIRECTORY).mkdir(parents=True, exist_ok=True)


def main(config_path=None):
    bfr = BusRoutesFixer(config_path)
    bfr.run_fixer()


def old():
    # a copy of the original steps for reference

    ## Save .tra, .net, .ver files from Scenario Management
    Visum = win32com.client.gencache.EnsureDispatch(
        "Visum.Visum.25")  # Visum = win32com.client.Dispatch("Visum.Visum.25")
    logging.info(f"PTV Visum started: {Visum}")
    C = win32com.client.constants
    this_project = Visum.ScenarioManagement.OpenProject(scenario_management_file)
    (old_mod_set, error_message_file_working) = copy_files_from_scenario_management(
        Visum, this_project, error_scenario_id, scenarios_path,
        working_scenario_name, error_scenario_network_file_name, error_message_log
    )
    ## Initialize classes and identify the error routes & nodes
    (error_route_mojibake, error_dirs, error_directions, error_nodes_check, error_route_names, error_route,
     error_nodes_class, node_check_list_class, error_route_list_class, check_node_pair_ok_class, fix_bus_route_class,
     num_of_routes, error_routes, error_nodes_type_check) = identify_errors(error_message_file,
                                                                            network_file_table_of_links,
                                                                            network_file_table_of_turns)

    ###### FIX ROUTE ERRORS
    ##  Load the working scenario to delete erroneous routes and create transfer files (1.deleted and 2.added)
    new_mod_delete_routes, mod_delete_routes_name, mod_delete_routes_file = prepare_visum_transferfile(
        Visum, scenario_management_path, this_project, working_scenario_name, num_of_routes, error_routes, error_dirs,
        error_directions, working_scenario_delete_routes_name, route_added_transfer_file_start,
        route_deleted_transfer_file
    )

    ##  Fix the routes in the transfer file (route_added_transfer_file_start)
    #   Identify the list of node pairs to check
    modification_check, node_links, error_node_stop_list, num_of_node_stop, error_route_list_long, error_node_list1, error_route_list, num_of_nodes, = get_node12ok_list(
        error_route_mojibake, RouteNodes, ErrorNodeList, ErrorNodeStopList, ModificationCheckList,
        route_added_transfer_file_start, error_scenario_network_file_name, network_file_table_of_links,
        network_file_table_of_turns, error_modification, error_nodes_check, error_nodes_type_check,
        check_node_pair_ok_class
    )
    ## Create a new .ver for shortest path search (where problematic routes have been deleted)
    all_messages, search_chains, nodes_delete_list, error_mod_transfer_file, routes_fixed_transfer_file = visum_path_search(
        C, working_scenario_delete_routes_name, error_modification, error_scenario_network_file_name, node_links,
        error_route_list, route_added_transfer_file_start, route_added_transfer_file_temp, fix_bus_route_class,
        route_added_transfer_file_final, modification_check, network_file_table_of_links, network_file_table_of_turns,
        check_node_pair_ok_class
    )

    ## copying final transfer files to mod files
    new_mod_no2, this_mod_name2, mod_file_name2, new_mod_no3, this_mod_name3, mod_file_name3, new_mod_set, cur_scenario_id, error_message_file_fixed = save_to_sm(
        this_project, scenario_management_path, processed_error_mod_transfer_file, route_added_transfer_file_final,
        old_mod_set, new_mod_delete_routes, error_message_path, Visum
    )

    ###### SHOW AND SAVE  WARNINGS IF THERE ARE ANY
    show_n_save_messages(all_messages)


if __name__ == "__main__":
    main()

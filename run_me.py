"""
# -*- coding: utf-8 -*-
This version addresses various route error types through shortest-path search including 'turn closed', 'no link', ''is blocked for the transport system''
Author: Shanshan Xie
Adapted from: P6FixBusRoute30.py (Birendra Shrestha)

Instructions:
- Step 1: Specify 'scenario_management_path', 'error_modification_id' & 'error_scenario_id' in the ../directories.json 
- Step 2: Run the main script 'run_me.py' 
"""

import logging
import shutil
#import tkinter as tk
#from tkinter import ttk
#from pathlib import Path

import win32com.client

# Import User's Inputs
from config.read_json import *
from source_code.node_checklist import NodeCheckList
from source_code.error_reading import ErrorNodes, ModificationCheckList
from source_code.route_nodes import RouteNodes
from source_code.error_node_stop_route_lists import ErrorNodeStopList, ErrorNodeList, ErrorRouteList
from source_code.check_node12_ok import CheckNodePairOk
from source_code.fix_bus_route import FixBusRoute
from logs.logger_configuration import *
from source_code.show_n_save_messages import show_n_save_messages

###### PREPARATIONS:
## Save .tra, .net, .ver files from Scenario Management
Visum = win32com.client.gencache.EnsureDispatch("Visum.Visum.25") # Visum = win32com.client.Dispatch("Visum.Visum.25")
logging.info(f"PTV Visum started: {Visum}")
C = win32com.client.constants
this_project = Visum.ScenarioManagement.OpenProject(scenario_management_file)
from source_code.copy_files_from_scenario_management import copy_files_from_scenario_management
(old_mod_set, error_message_file_working) = copy_files_from_scenario_management(
    Visum, this_project, error_scenario_id, scenarios_path,
    working_scenario_name, network_file_name, error_message_log
)
## Initialize classes and identify the error routes & nodes
from source_code.identify_error_routes import identify_errors
(error_route_mojibake, error_dirs, error_directions, error_nodes_check, error_route_names, error_route, error_nodes_class, node_check_list_class, error_route_list_class, check_node_pair_ok_class, fix_bus_route_class, num_of_routes, error_routes, error_nodes_type_check) = identify_errors(error_message_file, network_file_table_of_links, network_file_table_of_turns )

###### FIX ROUTE ERRORS
##  Load the working scenario to delete erroneous routes and create transfer files (1.deleted and 2.added)
from source_code.visum_pre_search_path import prepare_visum_transferfile
new_mode_delete_routes, mode_delete_routes_name, mode_delete_routes_file = prepare_visum_transferfile(
    Visum, this_project, working_scenario_name, num_of_routes, error_routes, error_dirs,
    error_directions, working_scenario_delete_routes_name, route_added_transfer_file_start,
    route_deleted_transfer_file
)

##  Fix the routes in the transfer file (route_added_transfer_file_start)
from source_code.get_node12ok_list import get_node12ok_list
modification_check, node_links, error_node_stop_list, num_of_node_stop, error_route_list_long, error_node_list1, error_route_list, num_of_nodes = get_node12ok_list(
    error_route_mojibake, RouteNodes, ErrorNodeList, ErrorNodeStopList, ModificationCheckList,  route_added_transfer_file_start, network_file_name, network_file_table_of_links, network_file_table_of_turns, error_modification, error_nodes_check, error_nodes_type_check, check_node_pair_ok_class
)
## Create a new .ver for shortest path search (where problematic routes have been deleted)
from source_code.visum_path_search import visum_path_search
all_messages, search_chains, nodes_delete_list, error_mod_transfer_file, routes_fixed_transfer_file = visum_path_search(
    C, working_scenario_delete_routes_name, error_modification, network_file_name, node_links, error_route_list, route_added_transfer_file_start, route_added_transfer_file_temp, fix_bus_route_class, route_added_transfer_file_final, modification_check
)

## copying final transfer files to mod files

from source_code.save_to_sm import save_to_sm
new_mod_no2, this_mod_name2, mod_file_name2, new_mod_no3, this_mod_name3, mod_file_name3, new_mod_set, cur_scenario_id, error_message_file_fixed = save_to_sm(
    this_project, error_mod_transfer_file, route_added_transfer_file_final, old_mod_set, new_mode_delete_routes, error_message_path, Visum
)

# show and save warning
show_n_save_messages(all_messages)

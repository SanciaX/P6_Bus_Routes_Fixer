"""
# -*- coding: utf-8 -*-
This version addresses various route error types through shortest-path search including 'turn closed', 'no link', ''is blocked for the transport system''
Author: Shanshan Xie
Adapted from: P6FixBusRoute30.py (Birendra Shrestha)

Instructions:
- Specify the modification IDs, directories and file names in 'user_inputs.py'.

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
from source_code.check_node12_ok import CheckNode12ok
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
    Visum, this_project, error_scenario_id, error_message_dir,
    working_scenario_name, network_file_name, error_message_log
)

from source_code.define_classes import initialize_classes

# Initialize classes and load error data
(error_dir_list, error_direction_list, error_nodes_check, error_route, error_node_class, node_check_list_class, error_route_list_class, node12ok_class, fix_bus_route_class, num_of_routes, error_route_list, error_nodes_type_check) = initialize_classes(error_message_file, network_file_name_short)

###### FIX ROUTE ERRORS

# STEP 1 Load the working scenario to delete erroneous routes and create transfer files (1.deleted and 2.added)
# route_deleted_transfer_file will be used as a new Modification
# route_added_transfer_file_start is where the routes will be fixed and then applied to the problematic
Visum.LoadVersion(working_scenario_name)  # load previously exported .ver file

for route_count in range(num_of_routes):
    error_route = error_route_list[route_count]
    error_dir = error_dir_list[route_count]
    error_direction = error_direction_list[route_count]

    error_route_name = f"{error_route} {error_dir}".strip()
    print(f"Error Route: {error_route} {error_dir} ")

    # Delete the Route in error file and save version
    route_to_delete = Visum.Net.LineRoutes.ItemByKey(error_route, error_direction, error_route_name)
    if route_to_delete:
        Visum.Net.RemoveLineRoute(route_to_delete)

Visum.SaveVersion(working_scenario_delete_routes_name)

# Create a transfer file *.tra file from b to a (destination)
Visum.GenerateModelTransferFileBetweenVersionFiles(
    working_scenario_delete_routes_name,
    working_scenario_name,
    route_added_transfer_file_start,
    LayoutFile="",
    NonDefaultOnly=False,
    NonEmptyTablesOnly=True,
    WriteLayoutIntoModelTransferFile=True,
)
Visum.GenerateModelTransferFileBetweenVersionFiles(
    working_scenario_name,
    working_scenario_delete_routes_name,
    route_deleted_transfer_file,
    LayoutFile="",
    NonDefaultOnly=False,
    NonEmptyTablesOnly=True,
    WriteLayoutIntoModelTransferFile=True,
)

# Create a new modification to delete the routes
new_modification1 = this_project.AddModification()
new_modification1.SetAttValue("Code", "Erroneous Routes Deleted")
new_modification1.SetAttValue(
    "Description", "Copied from the last working modification and have problematic routes deleted"
)
new_mod_no1 = int(new_modification1.AttValue("No"))
this_mod_name1 = new_modification1.AttValue("TraFile")

mod_file_name1 = (
        "C:\\Users\\Shanshan Xie\\TfL\\06 Scenario management\\SM_TESTING\\Modifications\\"
        + this_mod_name1
)
shutil.copy2(
    route_deleted_transfer_file, mod_file_name1
)  # copy the transper file to the path of the scenario management's Modification folder

###### Fix the routes in the transfer file (route_added_transfer_file_start)
route_node_class = RouteNodes(route_added_transfer_file_start)  # read from route_added_transfer_file_start
error_node_list_class = ErrorNodeList()
error_node_stop_list_class = ErrorNodeStopList()
route_node_class.read_route_file(
    error_node_list_class, error_node_stop_list_class
)  # get the list of odes and the nestedlist of nodes and stops / WITH OPEN(routeTransferFileStartName), WHICH IS A TRANSFER FILE THAT ADDS THE PROBLEM ROUTES
error_node_stop_list = error_node_stop_list_class.get_node_stop_list  # error_node_stop_list is a nested list
num_of_node_stop = error_node_stop_list_class.get_nodes_stop_count()
error_route_list_long = error_node_stop_list_class.get_route()
error_node_list1 = error_node_list_class.check_node1()
error_route_list = error_node_list_class.error_route_id()

num_of_nodes = error_node_list_class.error_num_nodes()
print(f"Number of nodes along the route(s): {num_of_nodes}")

start_marker = "$LINK:NO"
end_marker = "$LINKPOLY"
with open(network_file_name, "r") as fp:
    lines = fp.readlines()
in_between = False
result_lines = []
for line in lines:
    if start_marker in line:
        in_between = True  # Start keeping lines
    if in_between:
        result_lines.append(line)
    if end_marker in line:
        in_between = False  # Stop keeping lines
with open(network_file_name_short, "w") as output:
    output.writelines(result_lines)

counting_node = 0
node_links = []

# ! The pairs of nodes recognised through "for count in range(num_of_nodes-1)" iretation are all successive nodes along the original route
for count in range(num_of_nodes - 1):
    # print("Checking Count:", count)
    check_node1 = error_node_list1[count]
    check_node2 = error_node_list1[count + 1]
    check_route_this_node = error_route_list[count]
    check_route_of_next_node = error_route_list[count + 1]
    node12ok = node12ok_class.get_error_nodes2(
        count,
        check_node1,
        check_node2,
        check_route_this_node,
        check_route_of_next_node,
        error_nodes_check,
        error_nodes_type_check,
    )  # return 999 or 1 or the missing node that can be solved by Birendra's method
    """
    node12ok=1: node 1, 2 and the link, turn... from node1 to 2 are fine
    #node12ok=2: node 1 exists, node 2 doesn't exist, which will also leads to 'no link warning'
    #node12ok=3: node 1, 2 exist, but no link from 1 to 2 
    #node12ok=4: node 1, 2 exist, but Link close
    #node12ok=5: node 1, 2 and the link from 1 to 2 exist, but there are turn, lane, ... issues.
    """
    node_links.append([check_node1, check_node2, node12ok])

##### Problematic nodes read from the modification file (.tra)
modification_check = ModificationCheckList()
modification_check.set_links_to_check(error_modification,error_node_list1)
node_links_replace = modification_check.get_links_to_check()
node_links_replace = [[str(x), str(y), z] for x, y, z in node_links_replace]

# Update node_links with replacements
for replace in node_links_replace:
    for link in node_links:
        if replace[0] == link[0] and replace[1] == link[1]:
            link[2] = replace[2]

# Create a new .ver for shortest path search (where problematic routes have been deleted)
Visum2 = win32com.client.gencache.EnsureDispatch("Visum.Visum.25")
Visum2.LoadVersion(working_scenario_delete_routes_name)
Visum2.ApplyModelTransferFile(error_modification)
Visum2.IO.LoadNet(network_file_name, ReadAdditive=False)

# Messages in the widget
all_messages = ""

# Initialise variables to track state
n_found = False
a_n = None
search_chains = []  # the list of lists of nodes needing to be added to the route

for i in range(len(node_links)):
    # route_i = check_route_this_node[i]
    if node_links[i][2] != 1 and not n_found:
        a_n = node_links[i][0]  # Capture the first column value as a_n
        n_found = True  # We found a_n, now we search for a_m

    # Now we search for the row where the third column equals 1
    if node_links[i][2] == 1 and n_found:
        a_m = node_links[i][0]  # Capture the first column value as a_m
        # seachNode1n2.append((a_n, a_m))  # Append the tuple (a_n, a_m) to array1
        try:
            aNetElementContainer = Visum2.CreateNetElements()
            node1 = Visum2.Net.Nodes.ItemByKey(int(a_n))
            node2 = Visum2.Net.Nodes.ItemByKey(int(a_m))
            aNetElementContainer.Add(node1)
            aNetElementContainer.Add(node2)
            # Visum2.Net.Links.AddUserDefinedAttribute('ShortestPath','ShortestPath','ShortestPath',1)
            Visum2.Analysis.RouteSearchPrT.Execute(
                aNetElementContainer, "T", 0, IndexAttribute="SPath"
            )
            NodeChainPuT = Visum2.Analysis.RouteSearchPuTSys.NodeChainPuT
            NodeChain = Visum2.Analysis.RouteSearchPrT.NodeChainPrT
            chain = [error_route_list[i]]
            for n in range(len(NodeChain)):
                chain.append(NodeChain[n].AttValue("NO"))
            # Visum2.Analysis.RouteSearchPuTSys.Clear()
            if chain != [error_route_list[i]]:  # the first item being the route
                search_chains.append(chain)
            # Reset n_found to continue the process
            Visum2.Analysis.RouteSearchPrT.Clear()
        except Exception:
            message = f"Warning: Shortest Path is not found between {a_n} and {a_m}."
            all_messages += message + "\n"
        n_found = False

for sublist in search_chains:
    for i in range(1, len(sublist)):
        sublist[i] = int(sublist[i])

if search_chains:
    all_messages += "Dear Modeller: the following routes have been rerouted through shortest path. Please review the routes and make necessary changes"
for chain in search_chains:
    message = f"Route {chain[0]}: please review the route between {chain[1]} and {chain[-1]}"
    print(message)

nodes_delete_list = modification_check.get_nodes_to_delete()
if search_chains:
    shutil.copy2(
        route_added_transfer_file_start, route_transfer_file_temp_name
    )  # to keep the start file unchanged
    fix_bus_route_class.fix_routes(
        nodes_delete_list, search_chains, route_transfer_file_temp_name, route_added_transfer_file_final
    )
Visum3 = win32com.client.gencache.EnsureDispatch("Visum.Visum.25")
Visum3.LoadVersion(working_scenario_delete_routes_name)
# create AddNetRead-Object and specify desired conflict avoiding method
anrController = Visum3.IO.CreateAddNetReadController()
anrController.SetWhatToDo("Line", C.AddNetRead_OverWrite)
anrController.SetWhatToDo("LineRoute", C.AddNetRead_Ignore)
anrController.SetWhatToDo("LineRouteItem", C.AddNetRead_Ignore)
anrController.SetWhatToDo("TimeProfile", C.AddNetRead_Ignore)
anrController.SetWhatToDo("TimeProfileItem", C.AddNetRead_Ignore)
anrController.SetWhatToDo("VehJourney", C.AddNetRead_Ignore)
anrController.SetUseNumericOffset("VehJourney", True)
anrController.SetWhatToDo("VehJourneyItem", C.AddNetRead_DoNothing)
anrController.SetWhatToDo("VehJourneySection", C.AddNetRead_Ignore)
anrController.SetWhatToDo("ChainedUpVehJourneySection", C.AddNetRead_DoNothing)
anrController.SetWhatToDo("UserAttDef", C.AddNetRead_Ignore)
anrController.SetWhatToDo("Operator", C.AddNetRead_OverWrite)

anrController.SetConflictAvoidingForAll(10000, "ORG_")
# apply a model transfer
Visum3.ApplyModelTransferFile(error_modification, anrController)
Visum3.SaveVersion(working_scenario_load_error_mod)
Visum3.GenerateModelTransferFileBetweenVersionFiles(
    working_scenario_delete_routes_name,
    working_scenario_load_error_mod,
    error_mod_transfer_file,
    LayoutFile="",
    NonDefaultOnly=False,
    NonEmptyTablesOnly=True,
    WriteLayoutIntoModelTransferFile=True,
)

Visum3.ApplyModelTransferFile(route_added_transfer_file_final, anrController)
Visum3.SaveVersion(working_scenario_routes_fixed_name)
Visum3.GenerateModelTransferFileBetweenVersionFiles(
    working_scenario_load_error_mod,
    working_scenario_routes_fixed_name,
    routes_fixed_transfer_file,
    LayoutFile="",
    NonDefaultOnly=False,
    NonEmptyTablesOnly=True,
    WriteLayoutIntoModelTransferFile=True,
)

### copying final transfer files to mod files
# new error_modification
new_modification = this_project.AddModification()
new_modification.SetAttValue("Code", "Refined Problematic Modification")
new_modification.SetAttValue(
    "Description",
    "Copied from the modification with error, with the erroreous modiffication reloaded using conflict avoiding parameters",
)
new_mod_no2 = int(new_modification.AttValue("No"))
this_mod_name2 = new_modification.AttValue("TraFile")
mod_file_name2 = (
        "C:\\Users\\Shanshan Xie\\TfL\\06 Scenario management\\SM_TESTING\\Modifications\\"
        + this_mod_name2
)
shutil.copy2(error_mod_transfer_file, mod_file_name2)  # to keep the start file unchanged

# add the fixed routes
new_modification = this_project.AddModification()
new_modification.SetAttValue("Code", "Problematic Routes Re-added")
new_modification.SetAttValue("Description", "Have the deleted problematic routes added")
new_mod_no3 = int(new_modification.AttValue("No"))
this_mod_name3 = new_modification.AttValue("TraFile")

mod_file_name3 = (
        "C:\\Users\\Shanshan Xie\\TfL\\06 Scenario management\\SM_TESTING\\Modifications\\"
        + this_mod_name3
)
shutil.copy2(route_added_transfer_file_final, mod_file_name3)  # to keep the start file unchanged

###### apply the Modification with error

#old_mod_set = error_scenario.AttValue("MODIFICATIONS")
#print(old_mod_set)
new_mod_set = old_mod_set[:-1] + str(new_mod_no1) + "," + str(new_mod_no2) + "," + str(new_mod_no3)
#
print(new_mod_set)
# curScenario=this_project.Scenarios.ItemByKey(8)
curScenario = this_project.AddScenario()
curScenarioId = curScenario.AttValue("NO")
curScenario.SetAttValue("CODE", "BusRouteFixed")
curScenario.SetAttValue("PARAMETERSET", "1")
# curScenario.SetAttValue("MODIFICATIONS","1,2,3,5,7,11")##11 should be from new mod file and others from user input scenario
curScenario.SetAttValue("MODIFICATIONS", new_mod_set)
# error_message_file=error_message_dir+str(error_scenario_id)+".txt"
errorMessageFileFixed = error_message_dir + str(curScenarioId) + ".txt"  # new error file
Visum.SetErrorFile(errorMessageFileFixed)  # writing error message on a defined file
curScenario.LoadInput()


# show and save warning
show_n_save_messages(all_messages)

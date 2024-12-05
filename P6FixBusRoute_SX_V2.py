"""
Created on Thu Oct  3 11:58:01 2024

@author: Shanshan Xie
"""

# -*- coding: utf-8 -*-
"""
This version addresses various route error types through shortest-path search including 'turn closed', 'no link', ''is blocked for the transport system''

Author: Shanshan Xie
Adapted from: P6FixBusRoute30.py (Birendra Shrestha)

Instructions:
- Specify the IDs and paths in Section 1.1.
- Use debug mode and add breakpoints before the shortest path search.
- Go to the open .ver file to set the T_PUTSYS(W) and T_PUTSYS(B) of all links to 1 min.
"""

import os
import sys
import logging
import shutil
import platform
import win32com.client
import tkinter as tk
from tkinter import ttk

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log format
    datefmt="%Y-%m-%d %H:%M:%S",  # Date format
    filename="app.log",  # Log file name
    filemode="a",  # Append to the log file (use 'w' to overwrite)
)
logging.debug("Script run")

##############################################################################
# SECTION 1: Configuration
##############################################################################

# Section 1.1: User Input
error_scenario_id = 8  # Scenario with bus route issues
working_scenario_id = 2  # Last scenario without network errors
error_modification_id = 2  # First modification where the route errors occur

# Scenario management paths and files
scenario_management_file = (
    r"C:\\Users\\Shanshan Xie\\TfL\\06 Scenario management\\SM_TESTING\\SM_TESTING.vpdbx"
)
scenario_management_path = r"C:\\Users\\Shanshan Xie\\TfL\\06 Scenario management\\SM_TESTING"
bus_routes_fix_path = r"C:\\Users\\Shanshan Xie\\TfL\\06 Scenario management\\Bus_Routes_Fix"  # Temp folder for bus route fixes


##Section 1.2 Define files
# Error modification file in SM_TESTING folder
error_modification_list = list(scenario_management_path + r"\Modifications\M000000.tra")
error_modification_list[-len(str(error_modification_id)) - 4] = str(error_modification_id)
error_modification = "".join(error_modification_list)

# Find the error messages in the SM_TESTING folder
error_message_dir = scenario_management_path + r"\Scenarios\S000008"  # Dir of the error messages


# Message log
error_message_log = bus_routes_fix_path + r"\MessageLog.txt"

# .ver files
working_scenario_name = bus_routes_fix_path + r"\scenarioWorking.ver"
working_scenario_delete_routes_name = bus_routes_fix_path + r"\scenarioWorkingDeleteRoutes.ver"
working_scenario_load_error_mod = bus_routes_fix_path + r"\working_scenario_load_error_mod.ver"
working_scenario_routes_fixed_name = bus_routes_fix_path + r"\scenarioWorkingRoutesFixed.ver"
route_search_model = bus_routes_fix_path + r"\route_search_model.ver"

# .net files
network_file_name = bus_routes_fix_path + r"\NetworkFileError.net"
network_file_name_short = bus_routes_fix_path + r"\NetworkFileErrorShort.net"

# .tra files
route_deleted_transfer_file = bus_routes_fix_path + r"\routeDeletedTransfer.tra"
route_added_transfer_file_start = bus_routes_fix_path + r"\routeTransferFileStart.tra"
route_transfer_file_temp_name = bus_routes_fix_path + r"\routeTransferFileTemp.tra"
route_added_transfer_file_final = bus_routes_fix_path + r"\routeTransferFileFinal.tra"
routes_fixed_transfer_file = bus_routes_fix_path + r"\routeFixedTransferFile.tra"
error_mod_transfer_file = bus_routes_fix_path + r"\error_mod_transfer_file.tra"


#############################################################################
#############################################################################
###### SECTION 2: CLASSES & FUNCTIONS
########################################################
## Section 2.1: Read the Error Message



# class NodeCheckList: get the lists of Node1, Node2 on bus routes between which the link/turn may be problematic
class NodeCheckList:
    my_class_var_1 = "1"
    def __init__(self):
        self.anode1 = []
        self.anode2 = []
        self.routeName = []
        self.error_type = []

    def get_node_checklist(self, node1, node2, error_type):
        """

        :param node1:
        :param node2:
        :param error_type:
        :return: 
        """

        """Get the list of node pairs along the route between which the route is problematic and the error_type between them."""
        self.anode1 = self.anode1.append(node1)
        self.anode2 = self.anode2.append(node2)
        self.error_type = self.error_type.append(error_type)

    def get_check_node1(self):
        return self.anode1

    def get_check_node2(self):
        return self.anode2

    def get_error_type(self):
        """

        :return:
        """
        return self.error_type


# class ErrorNodes: read error message
class ErrorNodes:
    def __init__(self, error_message_file):
        self.error_message_file = error_message_file
        self.word = "Warning Line route"
        self.word1 = "Error Line route"
        self.word_turn = ": Turn"
        self.word_turn_block = "is blocked for the transport system" # e.g. Error Line route 168;168 SB;>: Turn 10037016->10048187->10026747 is blocked for the transport system B.
        # link close error
        self.word_link1 = "link"
        self.word_link2 = " closed for the transport system B" # e.g. Error Line route 176;176 NB;>: 2 links are closed for the transport system B. Affected links: 24000455(10010348->24000154); 24000456(24000154->10053158)
        self.word_no_link_provide = "Error No link provided between node"
        self.word_no_line_route_item_node = "Error No line route item was found at node"
        self.word_no_line_route_item_stop = "Error No line route item was found at stop point"
        self.word_mojibake = "Error Line route 1;1 EB;>: FORMATTING ERROR in: %1$l turns are closed for the transport system %2$s. Affected turns: %3$s"

    def read_error_file(self, errorRouteList_Class, node_check_list_class):
        with open(self.error_message_file, "r") as fp:
            lines = fp.readlines()

        counter1 = 0
        for line in lines:
            line = line.strip()

            if all(word in line for word in [self.word1, self.word_turn, self.word_turn_block]):
                parts = line.split("->")
                NodeT1 = parts[1][:8]
                NodeT2 = parts[2][:8]
                node_check_list_class.get_node_checklist(NodeT1, NodeT2, "Turn block")

            if all(word in line for word in [self.word_link1, self.word_link2]):
                numNodePair = line.count("(")
                for _ in range(numNodePair):
                    parts = line.split("(")
                    NodeT1 = parts[1][:8]
                    NodeT2 = parts[1].split(">")[1][:8]
                    node_check_list_class.get_node_checklist(NodeT1, NodeT2, "Link Close")
                    line = parts[1].split(")")[1]

            if self.word_no_link_provide in line:
                parts = line.split("node")
                NodeT1 = parts[1][1:9]
                NodeT2 = parts[2][1:9]
                node_check_list_class.get_node_checklist(NodeT1, NodeT2, "No Link")

            if self.word in line or self.word1 in line:
                startIndex = line.find(";") + 1
                spaceIndex = line.find(" ", startIndex)
                semiColonIndex = line.find(";")

                busRouteNumber = line[startIndex:spaceIndex]
                busRouteDir = line[spaceIndex + 1: spaceIndex + 3]
                direction = line[semiColonIndex + 1: semiColonIndex + 2]

                errorRouteList_Class.get_error_route(
                    counter1, busRouteNumber, busRouteDir, direction
                )
                counter1 += 1


########################################################
## Section 2.1: Recognise potential errors in the modification causing errors !!!!
class ModificationCheckList:
    def __init__(self):
        self.linkstocheck = []
        self.nodestoDelete = []

    def set_links_to_check(self, modificationfile):
        list0 = []
        nodesDelete = []
        with open(modificationfile, "r") as fp:
            lines = fp.readlines()
            inside_turn_block = False
            inside_link_block = False
            for line in lines:
                line = line.strip()

                if "TURN:FROMNODENO" in line:
                    inside_turn_block = True
                    continue

                if inside_turn_block:
                    if not line:
                        inside_turn_block = False
                    elif "B," not in line:
                        parts = line.split(";")
                        if len(parts) > 2:
                            n2, n3 = int(parts[1]), int(parts[2])
                            if any(
                                error_node_list1[i] == str(n2) and error_node_list1[i + 1] == str(n3)
                                for i in range(len(error_node_list1) - 1)
                            ):
                                list0.append([n2, n3, 5])

                if "LINK:" in line:
                    inside_link_block = True
                    continue

                if inside_link_block:
                    if not line:
                        inside_link_block = False
                    elif "B," not in line:
                        parts = line.split(";")
                        if len(parts) > 2:
                            n2, n3 = int(parts[1]), int(parts[2])
                            if any(
                                error_node_list1[i] == str(n2) and error_node_list1[i + 1] == str(n3)
                                for i in range(len(error_node_list1) - 1)
                            ):
                                list0.append([n2, n3, 4])

                if "Table: Nodes (deleted)" in line:
                    inside_link_block = True
                    continue

                if inside_link_block:
                    if not line:
                        inside_link_block = False
                    elif "*" not in line and "$" not in line:
                        n_missing = line
                        if any(
                            error_node_list1[i] == n_missing for i in range(len(error_node_list1) - 1)
                        ):
                            nodesDelete.append(n_missing)

        self.nodestoDelete = nodesDelete
        self.linkstocheck = list0

    def get_links_to_check(self):
        return self.linkstocheck

    def get_nodes_to_delete(self):
        return self.nodestoDelete


########################################################
## Section 2.3: Read the transfer file that adds fixed routes back

class RouteNodes:
    word3 = "$+LINEROUTEITEM"  # Start
    word4 = "$+TIMEPROFILE"  # End
    def __init__(self):
        self.routeNumber = 0

    def read_route_file(self, errorNodeList_Class, NodeStopList_Class):
        with open(route_added_transfer_file_start, "r") as fp:
            lines = fp.readlines()
            startLineIndex = False
            counter1 = -1
            counter2 = -1
            currentRoute = "0 "
            lastRoute = "0 "

            for line in lines:
                if word4 in line:
                    break
                if startLineIndex:
                    if "B;" in line:
                        NodeStop = line.split(";")[3:5]
                        counter2 += 1
                        NodeStopList_Class.get_node_stop(counter2, NodeStop, currentRoute)
                        nodeNum = line.split(";")[3]
                        currentRoute = line.split(";")[1]
                        if nodeNum.isdigit() and currentRoute == lastRoute:
                            counter1 += 1
                            errorNodeList_Class.get_error_nodes(counter1, nodeNum, currentRoute)
                        lastRoute = currentRoute
                if word3 in line:
                    startLineIndex = True

########################################################
## Section 2.4: Read the list of Nodes and Stops along the problematic route(s)
class error_node_stop_list:
    def __init__(self):
        self.get_node_stop_list = [[0, 0] for _ in range(10000)]
        self.route_name2 = [0] * 10000
        self.counter = 0

    def get_node_stop(self, counter, NodeStop, thisRoute):
        self.get_node_stop_list[counter] = NodeStop
        self.route_name2[counter] = thisRoute
        self.counter = counter

    def get_nodes_stop_count(self):
        return self.counter

    def get_from_stop(self):
        return self.get_node_stop_list[0][1]

    def get_to_stop(self):
        return self.get_node_stop_list[self.counter][1]

    def get_route(self):
        return self.route_name2

########################################################
## Section 2.5: Read the list of nodes along the problematic route(s)
class ErrorNodeList:
    def __init__(self):
        self.node1 = [0] * 10000
        self.node2 = [0] * 10000
        self.routeName = [0] * 10000
        self.counter = 0
        self.currentRoute = ["0 "] * 10000

    def get_error_nodes(self, counter, node1, currentRoute):
        self.node1[counter] = node1
        self.counter = counter
        self.currentRoute[counter] = currentRoute

    def check_node1(self):
        return self.node1

    def error_num_nodes(self):
        return self.counter  # num_of_nodes

    def error_route_id(self):
        return self.currentRoute

########################################################
## Section 2.6: the list of error routes
class error_route_list:
    def __init__(self):
        self.route_num = [0] * 100
        self.route_dir = [0] * 100
        self.route_direction = [0] * 100
        self.route_name_check = 0
        self.counting1 = 0

    def get_error_route(self, counterRoute, route_num, route_dir, route_direction):
        if counterRoute == 0:
            self.counting1 = 0
            self.route_num[self.counting1] = route_num
            self.route_dir[self.counting1] = route_dir
            self.route_direction[self.counting1] = route_direction
            self.route_name_check = route_num + route_direction

        if self.route_name_check != route_num + route_direction:
            self.counting1 += 1
            self.route_num[self.counting1] = route_num
            self.route_dir[self.counting1] = route_dir
            self.route_direction[self.counting1] = route_direction
            self.route_name_check = route_num + route_direction

    def error_route(self):
        return self.route_num

    def error_dir(self):
        return self.route_dir

    def error_direction(self):
        return self.route_direction

    def error_line_direction(self):
        return self.lineDirection

    def error_route_count(self):
        self.counting2 = self.counting1 + 1
        return self.counting2


########################################################
## Section 2.7: check if Node1, Node2 and the link in between is perfectly fine
class CheckNode12ok:
    def get_error_nodes2(
        self, counter, node11, node21, route_of_this_node, route_of_next_node, NodesCheck, NodesTypeCheck
    ):
        self.checkNode1 = (
            []
        )  # chekNodee1 is a list of Nodes that link to Node11 while Node21 has not been found to be linked to Node11
        self.check_node2 = (
            []
        )  # Nodes check_node2 is a list of Nodes that link to Node21. check_node2 would be empty if a link between Node11 & Node21 is found
        self.node11 = str(node11.strip())  #'10032516'
        self.node21 = str(node21.strip())  #'10040442'
        self.route_of_this_node = route_of_this_node
        self.route_of_next_node = route_of_next_node
        self.node12ok = 999  #
        with open(network_file_name_short, "r") as fp:
            lines = fp.readlines()
            node12ok = 0
            for line in lines:
                # check if node1 is present on a current line: if it's in, it will be added to checkNode1
                if (
                    route_of_this_node == route_of_next_node
                ):  # otherwise there is no need to search a path between node 1 and 2
                    if line.find(";B") != -1:  # check links with Bus system
                        if (
                            line.split(";")[1] == node11 and line.split(";")[2] == node21
                        ):  # when there's a link in the current network between two neighbour nodes along a line route
                            if ((node11, node21) in NodesCheck) == False:
                                node12ok = 1
                            else:
                                typeError = NodesTypeCheck[NodesCheck.index((node11, node21))][2]

                                if typeError == "Link Close":
                                    node12ok = 4
                                    print("Link Close:", node12ok)
                                elif typeError == "Turn block":
                                    node12ok == 5
                                    print("Turn block:", node12ok)
                                else:
                                    node12ok = -1
                                    print("Link exists but unknow Error between", node12ok)
        self.counter = counter
        self.node12ok = node12ok
        # logging.debug(f'Initialiased checkNode12ok with counter: {self.counter}, node11: {self.node11}, node21: {self.node21}')
        if self.node12ok == 999:
            print("No Link between ", node12ok)
        return self.node12ok


########################################################
## Section 2.8: Fix bus route in the transfer file
class FixBusRoute:
    def fix_routes(self, nodes_removal_list, chains, file_read, file_write):
        with open(file_write, "w") as fw, open(file_read, "r") as fp:
            lines = fp.readlines()
            inside_block = False
            new_lines = []

            for i, line in enumerate(lines):
                line = line.strip()
                if word3 in line:
                    inside_block = True
                elif word4 in line:
                    inside_block = False
                new_lines.append(line)

                if inside_block and i < len(lines) - 1:
                    next_line = lines[i + 1].strip()
                    if any(node in line for node in nodes_removal_list):
                        continue

                    for chain in chains:
                        first, second, *middle, last = chain
                        if (
                            str(first) in line
                            and str(second) in line
                            and str(first) in next_line
                            and str(last) in next_line
                        ):
                            new_lines.append(next_line)
                            for mid in middle:
                                new_lines.append(next_line.replace(str(last), str(mid)))
                            i += 1

            fw.write("\n".join(new_lines))


#############################################################################
#############################################################################
###### SECTION 3: PREPARATIONS: READ/COPY FILES AND DEFINE CLASSES
########################################################

########################################################
## Section 3.1: Copy (or read) .ver .net and .tra to the directory where the routes are fixed
# .ver: from which we load the network;
# .tra: from which we read and fix bus routes through adding or deleting nodes in Table: Line route items (inserted)
#  also we read additional potential errors from the modification where route errors arise from
#  meanwhile. we set
Visum = win32com.client.gencache.EnsureDispatch("Visum.Visum.24")
# Visum = win32com.client.Dispatch("Visum.Visum.24")
print("PTV Visum is started " + str(Visum))
C = win32com.client.constants
this_project = Visum.ScenarioManagement.OpenProject(scenario_management_file)
workingScenarioVersion = Visum.ScenarioManagement.CurrentProject.Scenarios.ItemByKey(
    working_scenario_id
)  # scenario with correct network check if it's 3 or 2
workingScenarioVersion.LoadInput()  # this command loads network of succesful scenario
Visum.SaveVersion(
    working_scenario_name
)  # save .ver file to (working_scenario_name, with the file's location specified in the beginning

# Create the latest *.net file with error (last scenario before error)
error_scenario = Visum.ScenarioManagement.CurrentProject.Scenarios.ItemByKey(
    error_scenario_id
)  # last scenario could be user input
error_scenario.LoadInput()  # this command Loads the input version file (base version and all modifications) for this scenario into the running Visum
Visum.IO.SaveNet(
    network_file_name,
    LayoutFile="",
    EditableOnly=True,
    NonDefaultOnly=True,
    ActiveNetElemsOnly=False,
    NonEmptyTablesOnly=True,
)
Visum.SetErrorFile(error_message_log)  # writing error message on a defined file
# error_scenario.LoadInput()

########################################################
## Section 3.2: Define objectives through Classes
error_node_class = ErrorNodes()  # read error message
node_check_list_class = NodeCheckList()
error_route_list_class = error_route_list()  # the list of error routes
error_node_class.read_error_file(
    error_route_list_class, node_check_list_class
)  # GET ERROR ROUTE: call error_route_list_class.get_error_route method, in which calls errorRouteList_Class.get_error_route(counter1,busRouteNumber,busRouteDir,direction)
error_route_list = error_route_list_class.error_route()  # Return route_num
error_dir_list = error_route_list_class.error_dir()
error_direction_list = error_route_list_class.error_direction()

error_nodes_checklist = node_check_list_class.get_check_node1()  # list of all the nodes to check
error_nodes_checklist2 = node_check_list_class.get_check_node2()
error_node_type_checklist = node_check_list_class.get_error_type()  # list of
error_nodes_check = [
    (error_nodes_checklist[i], error_nodes_checklist2[i]) for i in range(len(error_nodes_checklist))
]
error_nodes_type_check = [
    (error_nodes_checklist[i], error_nodes_checklist2[i], error_node_type_checklist[i])
    for i in range(len(error_nodes_checklist))
]
print(f"Nodes to check and error types: {error_nodes_type_check}")

node12ok_class = CheckNode12ok()
fix_bus_route_class = FixBusRoute()

num_of_routes = error_route_list_class.error_route_count()
error_route = error_route_list[1]
print(f"Number of Routes: {num_of_routes}")

#############################################################################
#############################################################################
###### SECTION 4: FIX ROUTE ERRORS
########################################################

# STEP 1 Load the working scenario to delete erroneous routes and create transfer files (1.deleted and 2.added)
# route_deleted_transfer_file will be used as a new Modification
# route_added_transfer_file_start is where the routes will be fixed and then applied to the problematic
Visum.LoadVersion(working_scenario_name)  # load previously exported .ver file

for route_count in range(num_of_routes):
    error_route = error_route_list[route_count]
    error_dir = error_dir_list[route_count]
    error_direction = error_direction_list[route_count]

    error_route_name = f"{error_route} {error_dir}".strip()
    print(f"Error Route: {error_route} {error_dir} {error_direction} {error_route_name}")

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


################################################
### Fix the routes in the transfer file (route_added_transfer_file_start)
route_node_class = RouteNodes()  # read from route_added_transfer_file_start
error_node_list_class = ErrorNodeList()
error_node_stop_list_class = error_node_stop_list()
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
    # print("Checkng Count:", count)
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
modification_check.set_links_to_check(error_modification)
node_links_replace = modification_check.get_links_to_check()
node_links_replace = [[str(x), str(y), z] for x, y, z in node_links_replace]

# Update node_links with replacements
for replace in node_links_replace:
    for link in node_links:
        if replace[0] == link[0] and replace[1] == link[1]:
            link[2] = replace[2]

# Create a new .ver for shortest path search (where problematic routes have been deleted)
Visum2 = win32com.client.gencache.EnsureDispatch("Visum.Visum")
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
            message = f"Warning: Shortest Path is not found between {a_n} and {a_m} for Bus Route {check_route_this_node}"
            all_messages += message + "\n"
        n_found = False

for sublist in search_chains:
    for i in range(1, len(sublist)):
        sublist[i] = int(sublist[i])

if search_chains != []:
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
Visum3 = win32com.client.gencache.EnsureDispatch("Visum.Visum")
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

old_mod_set = error_scenario.AttValue("MODIFICATIONS")
print(old_mod_set)
new_mod_set = old_mod_set[:-1] + str(new_mod_no1) + "," + str(new_mod_no2) + "," + str(new_mod_no3)
#
print(new_mod_set)
# curScenario=this_project.Scenarios.ItemByKey(8)
curScenario = this_project.AddScenario()
curScenarioNumber = curScenario.AttValue("NO")
curScenario.SetAttValue("CODE", "BusRouteFixed")
curScenario.SetAttValue("PARAMETERSET", "1")
# curScenario.SetAttValue("MODIFICATIONS","1,2,3,5,7,11")##11 should be from new mod file and others from user input scenario
curScenario.SetAttValue("MODIFICATIONS", new_mod_set)
# error_message_file=error_message_dir+str(error_scenario_id)+".txt"
errorMessageFile1 = error_message_dir + str(curScenarioNumber) + ".txt"  # new error file
Visum.SetErrorFile(errorMessageFile1)  # writing error message on a defined file
curScenario.LoadInput()


# show warning
def show_n_save_messages(all_messages):
    #save the logging message
    data_logger.info(all_messages)
    # Create the main window
    root = tk.Tk()
    root.title("Route Review Messages")

    # Create a frame to hold the Text widget and Scrollbar
    frame = ttk.Frame(root)
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Create a Scrollbar
    scrollbar = ttk.Scrollbar(frame)
    scrollbar.pack(side="right", fill="y")

    # Create a Text widget with a scrollbar
    text_widget = tk.Text(frame, wrap="word", yscrollcommand=scrollbar.set)
    text_widget.pack(fill="both", expand=True)

    # Configure the scrollbar
    scrollbar.config(command=text_widget.yview)

    # Insert the accumulated messages into the text widget in one go
    text_widget.insert(tk.END, all_messages)

    # Disable the text widget to prevent editing
    text_widget.config(state=tk.DISABLED)

    # Start the Tkinter event loop
    root.mainloop()


show_n_save_messages(all_messages)

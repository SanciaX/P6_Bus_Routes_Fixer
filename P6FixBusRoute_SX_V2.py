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
errorScenarioId = 8  # Scenario with bus route issues
workingScenarioId = 2  # Last scenario without network errors
errorModificationID = 2  # First modification where the route errors occur

# Scenario management paths and files
scenarioManagementFile = (
    r"C:\\Users\\Shanshan Xie\\TfL\\06 Scenario management\\SM_TESTING\\SM_TESTING.vpdbx"
)
scenarioManagementPath = r"C:\\Users\\Shanshan Xie\\TfL\\06 Scenario management\\SM_TESTING"
busRoutesFixPath = r"C:\\Users\\Shanshan Xie\\TfL\\06 Scenario management\\Bus_Routes_Fix"  # Temp folder for bus route fixes


##Section 1.2 Define files
# Error modification file in SM_TESTING folder
errorModificationList = list(scenarioManagementPath + r"\Modifications\M000000.tra")
errorModificationList[-len(str(errorModificationID)) - 4] = str(errorModificationID)
errorModification = "".join(errorModificationList)

# Find the error messages in the SM_TESTING folder
errorMessageDir = scenarioManagementPath + r"\Scenarios\S000008"  # Dir of the error messages
errorMessageFile = errorMessageDir + r"\Messages.txt"

# Message log
errorMessageLog = busRoutesFixPath + r"\MessageLog.txt"

# .ver files
workingScenarioName = busRoutesFixPath + r"\scenarioWorking.ver"
workingScenarioDeleteRoutesName = busRoutesFixPath + r"\scenarioWorkingDeleteRoutes.ver"
workingScenarioLoadErrorMod = busRoutesFixPath + r"\workingScenarioLoadErrorMod.ver"
workingScenarioRoutesFixedName = busRoutesFixPath + r"\scenarioWorkingRoutesFixed.ver"
RouteSearchVersion = busRoutesFixPath + r"\RouteSearchVersion.ver"

# .net files
networkFileName = busRoutesFixPath + r"\NetworkFileError.net"
networkFileNameShort = busRoutesFixPath + r"\NetworkFileErrorShort.net"

# .tra files
routeDeletedTransferFile = busRoutesFixPath + r"\routeDeletedTransfer.tra"
routeAddedTransferFileStart = busRoutesFixPath + r"\routeTransferFileStart.tra"
routeTransferFileTempName = busRoutesFixPath + r"\routeTransferFileTemp.tra"
routeAddedTransferFileFinal = busRoutesFixPath + r"\routeTransferFileFinal.tra"
routesFixedTransferFile = busRoutesFixPath + r"\routeFixedTransferFile.tra"
errorModTransferFile = busRoutesFixPath + r"\errorModTransferFile.tra"


#############################################################################
#############################################################################
###### SECTION 2: CLASSES & FUNCTIONS
########################################################
## Section 2.1: Read the Error Message

# key words
word = "Warning Line route"
word1 = "Error Line route"
wordTurn = ": Turn"
wordTurnBlock = "is blocked for the transport system"  # e.g. Error Line route 168;168 SB;>: Turn 10037016->10048187->10026747 is blocked for the transport system B.
# link close error
wordLink1 = "link"
wordLink2 = " closed for the transport system B"  # e.g. Error Line route 176;176 NB;>: 2 links are closed for the transport system B. Affected links: 24000455(10010348->24000154); 24000456(24000154->10053158)
wordNoLinkProvide = "Error No link provided between node"
### Remaining
wordNoLineRouteItemN = "Error No line route item was found at node"
wordNoLineRouteItemS = "Error No line route item was found at stop point"
wordMojibake = "Error Line route 1;1 EB;>: FORMATTING ERROR in: %1$l turns are closed for the transport system %2$s. Affected turns: %3$s"


# class NodeCheckList: get the lists of Node1, Node2 on bus routes between which the link/turn may be problematic
class NodeCheckList:
    MY_CLASS_VAR_1 = "1"
    def __init__(self):
        self.anode1 = []
        self.anode2 = []
        self.routeName = []
        self.errorType = []

    def get_node_checkList(self, node1, node2, errorType):
        """

        :param node1:
        :param node2:
        :param errorType:
        :return: 
        """

        """Get the list of node pairs along the route between which the route is problematic and the errorType between them."""
        self.anode1 = self.anode1.append(node1)
        self.anode2 = self.anode2.append(node2)
        self.errorType = self.errorType.append(errorType)

    def get_check_node1(self):
        return self.anode1

    def get_check_node2(self):
        return self.anode2

    def get_error_type(self):
        """

        :return:
        """
        return self.errorType


# class ErrorNodes: read error message
class ErrorNodes:
    def __init__(self):
        self.routeNumber = 0

    def read_error_file(self, errorRouteList_Class, nodeCheckList_Class):
        """Read the error message file and extract route and node data."""
        with open(errorMessageFile, "r") as fp:
            lines = fp.readlines()

        counter1 = 0
        for line in lines:
            line = line.strip()

            if all(word in line for word in [word1, wordTurn, wordTurnBlock]):
                parts = line.split("->")
                NodeT1 = parts[1][:8]
                NodeT2 = parts[2][:8]
                nodeCheckList_Class.get_node_checkList(NodeT1, NodeT2, "Turn block")

            if all(word in line for word in [wordLink1, wordLink2]):
                numNodePair = line.count("(")
                for _ in range(numNodePair):
                    parts = line.split("(")
                    NodeT1 = parts[1][:8]
                    NodeT2 = parts[1].split(">")[1][:8]
                    nodeCheckList_Class.get_node_checkList(NodeT1, NodeT2, "Link Close")
                    line = parts[1].split(")")[1]

            if wordNoLinkProvide in line:
                parts = line.split("node")
                NodeT1 = parts[1][1:9]
                NodeT2 = parts[2][1:9]
                nodeCheckList_Class.get_node_checkList(NodeT1, NodeT2, "No Link")

            if word in line or word1 in line:
                startIndex = line.find(";") + 1
                spaceIndex = line.find(" ", startIndex)
                semiColonIndex = line.find(";", startIndex)

                busRouteNumber = line[startIndex:spaceIndex]
                busRouteDir = line[spaceIndex + 1 : spaceIndex + 3]
                direction = line[semiColonIndex + 1 : semiColonIndex + 2]

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
                                errorNodeList1[i] == str(n2) and errorNodeList1[i + 1] == str(n3)
                                for i in range(len(errorNodeList1) - 1)
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
                                errorNodeList1[i] == str(n2) and errorNodeList1[i + 1] == str(n3)
                                for i in range(len(errorNodeList1) - 1)
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
                            errorNodeList1[i] == n_missing for i in range(len(errorNodeList1) - 1)
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
# Key words to locate to the correct table
word3 = "$+LINEROUTEITEM"  # Start
word4 = "$+TIMEPROFILE"  # End


class RouteNodes:
    def __init__(self):
        self.routeNumber = 0

    def read_route_file(self, errorNodeList_Class, NodeStopList_Class):
        with open(routeAddedTransferFileStart, "r") as fp:
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
class ErrorNodeStopList:
    def __init__(self):
        self.get_node_stop_list = [[0, 0] for _ in range(10000)]
        self.routeName2 = [0] * 10000
        self.counter = 0

    def get_node_stop(self, counter, NodeStop, thisRoute):
        self.get_node_stop_list[counter] = NodeStop
        self.routeName2[counter] = thisRoute
        self.counter = counter

    def get_nodes_stop_count(self):
        return self.counter

    def get_from_stop(self):
        return self.get_node_stop_list[0][1]

    def get_to_stop(self):
        return self.get_node_stop_list[self.counter][1]

    def get_route(self):
        return self.routeName2


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
        return self.counter  # numOfNodes

    def error_route_id(self):
        return self.currentRoute


########################################################
## Section 2.6: the list of error routes
class ErrorRouteList:
    def __init__(self):
        self.routeNum = [0] * 100
        self.routeDir = [0] * 100
        self.routeDirection = [0] * 100
        self.routeNameCheck = 0
        self.counting1 = 0

    def get_error_route(self, counterRoute, routeNum, routeDir, routeDirection):
        if counterRoute == 0:
            self.counting1 = 0
            self.routeNum[self.counting1] = routeNum
            self.routeDir[self.counting1] = routeDir
            self.routeDirection[self.counting1] = routeDirection
            self.routeNameCheck = routeNum + routeDirection

        if self.routeNameCheck != routeNum + routeDirection:
            self.counting1 += 1
            self.routeNum[self.counting1] = routeNum
            self.routeDir[self.counting1] = routeDir
            self.routeDirection[self.counting1] = routeDirection
            self.routeNameCheck = routeNum + routeDirection

    def error_route(self):
        return self.routeNum

    def error_dir(self):
        return self.routeDir

    def error_direction(self):
        return self.routeDirection

    def error_line_direction(self):
        return self.lineDirection

    def error_route_count(self):
        self.counting2 = self.counting1 + 1
        return self.counting2


########################################################
## Section 2.7: check if Node1, Node2 and the link in between is perfectly fine
class CheckNode12ok:
    def get_error_nodes2(
        self, counter, node11, node21, routeThisNode, routeNextNode, NodesCheck, NodesTypeCheck
    ):
        self.checkNode1 = (
            []
        )  # chekNodee1 is a list of Nodes that link to Node11 while Node21 has not been found to be linked to Node11
        self.checkNode2 = (
            []
        )  # Nodes checkNode2 is a list of Nodes that link to Node21. checkNode2 would be empty if a link between Node11 & Node21 is found
        self.node11 = str(node11.strip())  #'10032516'
        self.node21 = str(node21.strip())  #'10040442'
        self.routeThisNode = routeThisNode
        self.routeNextNode = routeNextNode
        self.node12ok = 999  #
        with open(networkFileNameShort, "r") as fp:
            lines = fp.readlines()
            node12ok = 0
            for line in lines:
                # check if node1 is present on a current line: if it's in, it will be added to checkNode1
                if (
                    routeThisNode == routeNextNode
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
thisProject = Visum.ScenarioManagement.OpenProject(scenarioManagementFile)
workingScenarioVersion = Visum.ScenarioManagement.CurrentProject.Scenarios.ItemByKey(
    workingScenarioId
)  # scenario with correct network check if it's 3 or 2
workingScenarioVersion.LoadInput()  # this command loads network of succesful scenario
Visum.SaveVersion(
    workingScenarioName
)  # save .ver file to (workingScenarioName, with the file's location specified in the beginning

# Create the latest *.net file with error (last scenario before error)
errorScenario = Visum.ScenarioManagement.CurrentProject.Scenarios.ItemByKey(
    errorScenarioId
)  # last scenario could be user input
errorScenario.LoadInput()  # this command Loads the input version file (base version and all modifications) for this scenario into the running Visum
Visum.IO.SaveNet(
    networkFileName,
    LayoutFile="",
    EditableOnly=True,
    NonDefaultOnly=True,
    ActiveNetElemsOnly=False,
    NonEmptyTablesOnly=True,
)
Visum.SetErrorFile(errorMessageLog)  # writing error message on a defined file
# errorScenario.LoadInput()

########################################################
## Section 3.2: Define objectives through Classes
errorNodeClass = ErrorNodes()  # read error message
nodeCheckList_Class = NodeCheckList()
errorRouteListClass = ErrorRouteList()  # the list of error routes
errorNodeClass.read_error_file(
    errorRouteListClass, nodeCheckList_Class
)  # GET ERROR ROUTE: call errorRouteListClass.get_error_route method, in which calls errorRouteList_Class.get_error_route(counter1,busRouteNumber,busRouteDir,direction)
errorRouteList = errorRouteListClass.error_route()  # Return routeNum
errorDirList = errorRouteListClass.error_dir()
errorDirectionList = errorRouteListClass.error_direction()

errorNodesChecklist = nodeCheckList_Class.get_check_node1()  # list of all the nodes to check
errorNodesChecklist2 = nodeCheckList_Class.get_check_node2()
errorNodeTypeChecklist = nodeCheckList_Class.get_error_type()  # list of
errorNodesCheck = [
    (errorNodesChecklist[i], errorNodesChecklist2[i]) for i in range(len(errorNodesChecklist))
]
errorNodesTypeCheck = [
    (errorNodesChecklist[i], errorNodesChecklist2[i], errorNodeTypeChecklist[i])
    for i in range(len(errorNodesChecklist))
]
print(f"Nodes to check and error types: {errorNodesTypeCheck}")

node12okClass = CheckNode12ok()
fixBusRouteClass = FixBusRoute()

numOfRoutes = errorRouteListClass.error_route_count()
errorRoute = errorRouteList[1]
print(f"Number of Routes: {numOfRoutes}")

#############################################################################
#############################################################################
###### SECTION 4: FIX ROUTE ERRORS
########################################################

# STEP 1 Load the working scenario to delete erroneous routes and create transfer files (1.deleted and 2.added)
# routeDeletedTransferFile will be used as a new Modification
# routeAddedTransferFileStart is where the routes will be fixed and then applied to the problematic
Visum.LoadVersion(workingScenarioName)  # load previously exported .ver file

for routeCount in range(numOfRoutes):
    errorRoute = errorRouteList[routeCount]
    errorDir = errorDirList[routeCount]
    errorDirection = errorDirectionList[routeCount]

    errorRouteName = f"{errorRoute} {errorDir}".strip()
    print(f"Error Route: {errorRoute} {errorDir} {errorDirection} {errorRouteName}")

    # Delete the Route in error file and save version
    routeToDelete = Visum.Net.LineRoutes.ItemByKey(errorRoute, errorDirection, errorRouteName)
    if routeToDelete:
        Visum.Net.RemoveLineRoute(routeToDelete)

Visum.SaveVersion(workingScenarioDeleteRoutesName)

# Create a transfer file *.tra file from b to a (destination)
Visum.GenerateModelTransferFileBetweenVersionFiles(
    workingScenarioDeleteRoutesName,
    workingScenarioName,
    routeAddedTransferFileStart,
    LayoutFile="",
    NonDefaultOnly=False,
    NonEmptyTablesOnly=True,
    WriteLayoutIntoModelTransferFile=True,
)
Visum.GenerateModelTransferFileBetweenVersionFiles(
    workingScenarioName,
    workingScenarioDeleteRoutesName,
    routeDeletedTransferFile,
    LayoutFile="",
    NonDefaultOnly=False,
    NonEmptyTablesOnly=True,
    WriteLayoutIntoModelTransferFile=True,
)


# Create a new modification to delete the routes
newModification1 = thisProject.AddModification()
newModification1.SetAttValue("Code", "Erroneous Routes Deleted")
newModification1.SetAttValue(
    "Description", "Copied from the last working modification and have problematic routes deleted"
)
newModNo1 = int(newModification1.AttValue("No"))
thisModName1 = newModification1.AttValue("TraFile")

modFileName1 = (
    "C:\\Users\\Shanshan Xie\\TfL\\06 Scenario management\\SM_TESTING\\Modifications\\"
    + thisModName1
)
shutil.copy2(
    routeDeletedTransferFile, modFileName1
)  # copy the transper file to the path of the scenario management's Modification folder


################################################
### Fix the routes in the transfer file (routeAddedTransferFileStart)
routeNodeClass = RouteNodes()  # read from routeAddedTransferFileStart
errorNodeListClass = ErrorNodeList()
errorNodeStopListClass = ErrorNodeStopList()
routeNodeClass.read_route_file(
    errorNodeListClass, errorNodeStopListClass
)  # get the list of odes and the nestedlist of nodes and stops / WITH OPEN(routeTransferFileStartName), WHICH IS A TRANSFER FILE THAT ADDS THE PROBLEM ROUTES
errorNodeStopList = errorNodeStopListClass.get_node_stop_list  # errorNodeStopList is a nested list
numOfNodeStop = errorNodeStopListClass.get_nodes_stop_count()
errorRouteListLong = errorNodeStopListClass.get_route()
errorNodeList1 = errorNodeListClass.check_node1()
errorRouteList = errorNodeListClass.error_route_id()

numOfNodes = errorNodeListClass.error_num_nodes()
print(f"Number of nodes along the route(s): {numOfNodes}")

start_marker = "$LINK:NO"
end_marker = "$LINKPOLY"
with open(networkFileName, "r") as fp:
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
with open(networkFileNameShort, "w") as output:
    output.writelines(result_lines)

countingNode = 0
nodelinks = []

# ! The pairs of nodes recognised through "for count in range(numOfNodes-1)" iretation are all successive nodes along the original route
for count in range(numOfNodes - 1):
    print("Checkng Count:", count)
    check_node1 = errorNodeList1[count]
    checkNode2 = errorNodeList1[count + 1]
    checkRouteThisNode = errorRouteList[count]
    checkRouteNextNode = errorRouteList[count + 1]
    node12ok = node12okClass.get_error_nodes2(
        count,
        check_node1,
        checkNode2,
        checkRouteThisNode,
        checkRouteNextNode,
        errorNodesCheck,
        errorNodesTypeCheck,
    )  # return 999 or 1 or the missing node that can be solved by Birendra's method
    """
    node12ok=1: node 1, 2 and the link, turn... from node1 to 2 are fine
    #node12ok=2: node 1 exists, node 2 doesn't exist, which will also leads to 'no link warning'
    #node12ok=3: node 1, 2 exist, but no link from 1 to 2 
    #node12ok=4: node 1, 2 exist, but Link close
    #node12ok=5: node 1, 2 and the link from 1 to 2 exist, but there are turn, lane, ... issues.
    """
    nodelinks.append([check_node1, checkNode2, node12ok])

##### Problematic nodes read from the modification file (.tra)
modificationCheck = ModificationCheckList()
modificationCheck.set_links_to_check(errorModification)
nodelinksReplace = modificationCheck.get_links_to_check()
nodelinksReplace = [[str(x), str(y), z] for x, y, z in nodelinksReplace]

# Update nodelinks with replacements
for replace in nodelinksReplace:
    for link in nodelinks:
        if replace[0] == link[0] and replace[1] == link[1]:
            link[2] = replace[2]

# Create a new .ver for shortest path search (where problematic routes have been deleted)
Visum2 = win32com.client.gencache.EnsureDispatch("Visum.Visum")
Visum2.LoadVersion(workingScenarioDeleteRoutesName)
Visum2.ApplyModelTransferFile(errorModification)
Visum2.IO.LoadNet(networkFileName, ReadAdditive=False)

# Messages in the widget
all_messages = ""

# Initialise variables to track state
n_found = False
a_n = None
searchChains = []  # the list of lists of nodes needing to be added to the route

for i in range(len(nodelinks)):
    # route_i = checkRouteThisNode[i]
    if nodelinks[i][2] != 1 and not n_found:
        a_n = nodelinks[i][0]  # Capture the first column value as a_n
        n_found = True  # We found a_n, now we search for a_m

    # Now we search for the row where the third column equals 1
    if nodelinks[i][2] == 1 and n_found:
        a_m = nodelinks[i][0]  # Capture the first column value as a_m
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
            chain = [errorRouteList[i]]
            for n in range(len(NodeChain)):
                chain.append(NodeChain[n].AttValue("NO"))
            # Visum2.Analysis.RouteSearchPuTSys.Clear()
            if chain != [errorRouteList[i]]:  # the first item being the route
                searchChains.append(chain)
            # Reset n_found to continue the process
            Visum2.Analysis.RouteSearchPrT.Clear()
        except Exception:
            message = f"Warning: Shortest Path is not found between {a_n} and {a_m} for Bus Route {checkRouteThisNode}"
            all_messages += message + "\n"
        n_found = False

for sublist in searchChains:
    for i in range(1, len(sublist)):
        sublist[i] = int(sublist[i])

if searchChains != []:
    all_messages += "Dear Modeller: the following routes have been rerouted through shortest path. Please review the routes and make necessary changes"
for chain in searchChains:
    message = f"Route {chain[0]}: please review the route between {chain[1]} and {chain[-1]}"
    print(message)

nodesDeleteList = modificationCheck.get_nodes_to_delete()
if searchChains:
    shutil.copy2(
        routeAddedTransferFileStart, routeTransferFileTempName
    )  # to keep the start file unchanged
    fixBusRouteClass.fix_routes(
        nodesDeleteList, searchChains, routeTransferFileTempName, routeAddedTransferFileFinal
    )
Visum3 = win32com.client.gencache.EnsureDispatch("Visum.Visum")
Visum3.LoadVersion(workingScenarioDeleteRoutesName)
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
Visum3.ApplyModelTransferFile(errorModification, anrController)
Visum3.SaveVersion(workingScenarioLoadErrorMod)
Visum3.GenerateModelTransferFileBetweenVersionFiles(
    workingScenarioDeleteRoutesName,
    workingScenarioLoadErrorMod,
    errorModTransferFile,
    LayoutFile="",
    NonDefaultOnly=False,
    NonEmptyTablesOnly=True,
    WriteLayoutIntoModelTransferFile=True,
)


Visum3.ApplyModelTransferFile(routeAddedTransferFileFinal, anrController)
Visum3.SaveVersion(workingScenarioRoutesFixedName)
Visum3.GenerateModelTransferFileBetweenVersionFiles(
    workingScenarioLoadErrorMod,
    workingScenarioRoutesFixedName,
    routesFixedTransferFile,
    LayoutFile="",
    NonDefaultOnly=False,
    NonEmptyTablesOnly=True,
    WriteLayoutIntoModelTransferFile=True,
)


### copying final transfer files to mod files
# new errorModification
newModification = thisProject.AddModification()
newModification.SetAttValue("Code", "Refined Problematic Modification")
newModification.SetAttValue(
    "Description",
    "Copied from the modification with error, with the erroreous modiffication reloaded using conflict avoiding parameters",
)
newModNo2 = int(newModification.AttValue("No"))
thisModName2 = newModification.AttValue("TraFile")
modFileName2 = (
    "C:\\Users\\Shanshan Xie\\TfL\\06 Scenario management\\SM_TESTING\\Modifications\\"
    + thisModName2
)
shutil.copy2(errorModTransferFile, modFileName2)  # to keep the start file unchanged

# add the fixed routes
newModification = thisProject.AddModification()
newModification.SetAttValue("Code", "Problematic Routes Re-added")
newModification.SetAttValue("Description", "Have the deleted problematic routes added")
newModNo3 = int(newModification.AttValue("No"))
thisModName3 = newModification.AttValue("TraFile")

modFileName3 = (
    "C:\\Users\\Shanshan Xie\\TfL\\06 Scenario management\\SM_TESTING\\Modifications\\"
    + thisModName3
)
shutil.copy2(routeAddedTransferFileFinal, modFileName3)  # to keep the start file unchanged

###### apply the Modification with error

oldModSet = errorScenario.AttValue("MODIFICATIONS")
print(oldModSet)
newModSet = oldModSet[:-1] + str(newModNo1) + "," + str(newModNo2) + "," + str(newModNo3)
#
print(newModSet)
# curScenario=thisProject.Scenarios.ItemByKey(8)
curScenario = thisProject.AddScenario()
curScenarioNumber = curScenario.AttValue("NO")
curScenario.SetAttValue("CODE", "BusRouteFixed")
curScenario.SetAttValue("PARAMETERSET", "1")
# curScenario.SetAttValue("MODIFICATIONS","1,2,3,5,7,11")##11 should be from new mod file and others from user input scenario
curScenario.SetAttValue("MODIFICATIONS", newModSet)
# errorMessageFile=errorMessageDir+str(errorScenarioId)+".txt"
errorMessageFile1 = errorMessageDir + str(curScenarioNumber) + ".txt"  # new error file
Visum.SetErrorFile(errorMessageFile1)  # writing error message on a defined file
curScenario.LoadInput()


# show warning
def show_messages(all_messages):
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


show_messages(all_messages)

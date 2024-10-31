"""
# -*- coding: utf-8 -*-
This version addresses various route error types through shortest-path search including 'turn closed', 'no link', ''is blocked for the transport system''
Author: Shanshan Xie
Adapted from: P6FixBusRoute30.py (Birendra Shrestha)

Instructions:
- Specify the modification IDs, directories and file names in 'user_inputs.py'.

"""

#import logging
import shutil
#import tkinter as tk
#from tkinter import ttk
#from pathlib import Path

import win32com.client

# Import User's Inputs
from user_inputs import *

from node_checklist import NodeCheckList
from error_reading import ErrorNodes, ModificationCheckList
from route_nodes import RouteNodes
from error_node_stop_route_lists import ErrorNodeStopList, ErrorNodeList, ErrorRouteList
from check_node12_ok import CheckNode12ok
from fix_bus_route import FixBusRoute
from logger_configuration import *
from show_n_save_messages import show_n_save_messages

###### PREPARATIONS: READ/COPY FILES FROM SCENARIO MANAGEMENT AND DEFINE CLASSES
# Initialise PTV COM object
Visum = win32com.client.gencache.EnsureDispatch("Visum.Visum.24")
# Visum = win32com.client.Dispatch("Visum.Visum.24")
logging.info(f"PTV Visum started: {Visum}")

# Load Scenario Management
C = win32com.client.constants
thisProject = Visum.ScenarioManagement.OpenProject(scenarioManagementFile)
workingScenarioVersion = Visum.ScenarioManagement.CurrentProject.Scenarios.ItemByKey(workingScenarioId)  # scenario with correct network
workingScenarioVersion.LoadInput()  # load the network of the last  working scenario
Visum.SaveVersion(workingScenarioName)  # save version file

# Load the *.net file with error
errorScenario = Visum.ScenarioManagement.CurrentProject.Scenarios.ItemByKey(errorScenarioId)
errorScenario.LoadInput()  # Loads the input version files (base version and all modifications) for this scenario
Visum.IO.SaveNet(
    networkFileName,
    LayoutFile="",
    EditableOnly=True,
    NonDefaultOnly=True,
    ActiveNetElemsOnly=False,
    NonEmptyTablesOnly=True,
)
Visum.SetErrorFile(errorMessageLog)  # set error log

# Initialise classes and load error data
errorNodeClass = ErrorNodes(errorMessageFile)  # read error message
nodeCheckList_Class = NodeCheckList()
errorRouteListClass = ErrorRouteList()  # the list of error routes

# Read error file and process routes
errorNodeClass.read_error_file(errorRouteListClass, nodeCheckList_Class)  # get error route: call errorRouteListClass.get_error_route method, in which calls errorRouteList_Class.get_error_route(counter1,busRouteNumber,busRouteDir,direction)
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

node12okClass = CheckNode12ok(networkFileNameShort)
fixBusRouteClass = FixBusRoute()

numOfRoutes = errorRouteListClass.error_route_count()
errorRoute = errorRouteList[1]
print(f"Number of Routes: {numOfRoutes}")

###### FIX ROUTE ERRORS

# STEP 1 Load the working scenario to delete erroneous routes and create transfer files (1.deleted and 2.added)
# routeDeletedTransferFile will be used as a new Modification
# routeAddedTransferFileStart is where the routes will be fixed and then applied to the problematic
Visum.LoadVersion(workingScenarioName)  # load previously exported .ver file

for routeCount in range(numOfRoutes):
    errorRoute = errorRouteList[routeCount]
    errorDir = errorDirList[routeCount]
    errorDirection = errorDirectionList[routeCount]

    errorRouteName = f"{errorRoute} {errorDir}".strip()
    print(f"Error Route: {errorRoute} {errorDir} ")

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

###### Fix the routes in the transfer file (routeAddedTransferFileStart)
routeNodeClass = RouteNodes(routeAddedTransferFileStart)  # read from routeAddedTransferFileStart
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
    # print("Checking Count:", count)
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
modificationCheck.set_links_to_check(errorModification,errorNodeList1)
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
            message = f"Warning: Shortest Path is not found between {a_n} and {a_m}."
            all_messages += message + "\n"
        n_found = False

for sublist in searchChains:
    for i in range(1, len(sublist)):
        sublist[i] = int(sublist[i])

if searchChains:
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


# show and save warning
show_n_save_messages(all_messages)

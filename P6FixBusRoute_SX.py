# -*- coding: utf-8 -*-
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
from tkinter import messagebox

# Configure logging
logging.basicConfig(level=logging.DEBUG)

##############################################################################
# SECTION 1: Configuration
##############################################################################

# Section 1.1: User Input
errorScenarioId = 8  # Scenario with bus route issues
workingScenarioId = 2  # Last scenario without network errors
errorModificationID = 2  # First modification where the route errors occur

# Scenario management paths and files
scenarioManagementFile = r"C:\\Users\\Shanshan Xie\\TfL\\06 Scenario management\\SM_TESTING\\SM_TESTING.vpdbx"
scenarioManagementPath = r"C:\\Users\\Shanshan Xie\\TfL\\06 Scenario management\\SM_TESTING"
busRoutesFixPath = r"C:\\Users\\Shanshan Xie\\TfL\\06 Scenario management\\Bus_Routes_Fix"  # Temp folder for bus route fixes


##Section 1.2 Define files
    # Error modification file in SM_TESTING folder
errorModificationList = list(scenarioManagementPath + r"\Modifications\M000000.tra")
errorModificationList[-len(str(errorModificationID))-4]=str(errorModificationID)
errorModification=''.join(errorModificationList)

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
word = 'Warning Line route'
word1 = 'Error Line route'
wordTurn = ': Turn'
wordTurnBlock = 'is blocked for the transport system'# e.g. Error Line route 168;168 SB;>: Turn 10037016->10048187->10026747 is blocked for the transport system B.
    # link close error
wordLink1 = 'link'
wordLink2 = ' closed for the transport system B'# e.g. Error Line route 176;176 NB;>: 2 links are closed for the transport system B. Affected links: 24000455(10010348->24000154); 24000456(24000154->10053158)
wordNoLinkProvide='Error No link provided between node'
    ### Remaining
wordNoLineRouteItemN='Error No line route item was found at node'
wordNoLineRouteItemS='Error No line route item was found at stop point'
wordMojibake='Error Line route 1;1 EB;>: FORMATTING ERROR in: %1$l turns are closed for the transport system %2$s. Affected turns: %3$s'

    # class NodeCheckList: get the lists of Node1, Node2 on bus routes between which the link/turn may be problematic
class NodeCheckList:
    def __init__(self):
        self.anode1=[]
        self.anode2=[]
        self.routeName=[]
        self.errorType = []
        
    def getNodeCheckList(self,node1,node2, errorType):
        self.anode1= self.anode1.append(node1)
        self.anode2= self.anode2.append(node2)
        self.errorType=self.errorType.append(errorType);
        
    def getcheckNode1(self):
        return self.anode1
    
    def getcheckNode2(self):
        return self.anode2
    
    def getErrorType(self):
        return self.errorType
    
    # class ErrorNodes: read error message
class ErrorNodes:
    def __init__(self):
        self.routeNumber = 0
        
    def ReadErrorFile(self,errorRouteList_Class,nodeCheckList_Class):
        with open(errorMessageFile, 'r') as fp:
            lines = fp.readlines()
            busRouteNumber=[0]*10
            counter1=0
            for line in lines:            
                if line.find(word1) != -1 and line.find(wordTurn) != -1 and line.find(wordTurnBlock) != -1:
                    NodeT1=line.split('->')[1][:8] #turn error Node 1
                    NodeT2=line.split('->')[2][:8] #turn error Node 2
                    errorType = 'Turn block'
                    nodeCheckList_Class.getNodeCheckList(NodeT1,NodeT2, errorType)                               
                if line.find(wordLink1) != -1 and line.find(wordLink2) != -1:
                    numNodePair = line.count('(')
                    nodeindex=0
                    for i in range(numNodePair):
                        if nodeindex < numNodePair:
                            NodeT1=line.split('(')[1][0:8] 
                            NodeT2=line.split('>')[1][0:8] 
                            errorType = 'Link Close'
                            nodeCheckList_Class.getNodeCheckList(NodeT1,NodeT2,errorType)
                            line = line.split(')')[1]
                            nodeindex+=1
                if line.find(wordNoLinkProvide) != -1:
                    NodeT1=line.split('node')[1][1:9] # 
                    NodeT2=line.split('node')[2][1:9] #
                    errorType = 'No Link'
                    nodeCheckList_Class.getNodeCheckList(NodeT1,NodeT2,errorType) #e.g. Error Line route 176;176 NB;>: 2 links are closed for the transport system B. Affected links: 24000455(10010348->24000154); 24000456(24000154->10053158)                    
                if line.find(word) != -1  or line.find(word1) != -1:           
                    startIndex = line.find(';')+1
                    blankString = " "                   
                    for i in range(len(line)):
                        j = line.find(blankString,startIndex)
                        if(j!=-1):
                            spaceIndex=j

                        k = line.find(";",startIndex)
                        if(k!=-1):
                            semiColonIndex=k
                    busRouteNumber= line[startIndex:spaceIndex]
                    busRouteDir= line[spaceIndex+1:spaceIndex+1+2]
                    direction=line[semiColonIndex+1:semiColonIndex+2]
                    errorRouteList_Class.getErrorRoute(counter1,busRouteNumber,busRouteDir,direction)
                    counter1+=1

########################################################
## Section 2.1: Recognise potential errors in the modification causing errors !!!!
class ModificationCheckList:
    def _init_(self):
        self.linkstocheck=[] 
        self.nodestoDelete=[]
        # potential node errors,  turn errors, potential stop errors
        
    def setLinkstoCheck(self, modificationfile):
        array0 = []
        nodesDelete=[]
        with open(modificationfile, 'r') as fp:
            lines = fp.readlines()
            inside_turn_block = False
            inside_link_block = False            
            for line in lines:
                line = line.strip() 
                
                ## Check for TURN:FROMNODENO block
                if 'TURN:FROMNODENO' in line:
                    # When 'TURN:FROMNODENO' is found, reset inside_turn_block and set n1
                    inside_turn_block = True
                    #n1 = int(line.split(';')[1])  # Get the second number as n1
                    continue  # Move to the next line                
                if inside_turn_block:
                    if line == '':
                        # If we encounter an empty line, we exit this block
                        inside_turn_block = False
                    elif 'B,' not in line:
                        # If the line doesn't contain 'B,', process it
                        parts = line.split(';')
                        if len(parts) > 2:
                            n2 = int(parts[1])  # Get the second number
                            n3 = int(parts[2])  # Get the third number
                            for i in range(len(errorNodeList1) - 1):  # Iterate over the list, stopping one element before the end
                                if errorNodeList1[i] == str(n2) and errorNodeList1[i + 1] == str(n3):
                                    array0.append([n2, n3, 5])  # Append [n1, n2, 5] to array0
                            
                ## Check for LINK: block
                if 'LINK:' in line:
                    # Reset the state for 'LINK:' block
                    inside_link_block = True
                    continue  # Move to the next line
                
                if inside_link_block:
                    if line == '':
                        # If we encounter an empty line, we exit this block
                        inside_link_block = False
                    elif 'B,' not in line:
                        # If the line doesn't contain 'B,', process it
                        parts = line.split(';')
                        if len(parts) > 2:
                            n2 = int(parts[1])  # Get the second number
                            n3 = int(parts[2])  # Get the third number
                            for i in range(len(errorNodeList1) - 1):  # Iterate over the list, stopping one element before the end
                                if errorNodeList1[i] == str(n2) and errorNodeList1[i + 1] == str(n3):
                                    array0.append([n2, n3, 4])  # Append [n2, n3, 4] to array0                
                
                ## Check Nodes (deleted) Table
                if 'Table: Nodes (deleted)' in line:
                    inside_link_block = True
                    continue
                if inside_link_block:
                    if line =='':
                        inside_link_block = False
                    elif ('*' not in line) and ('$' not in line):
                        n_missing = line
                        for i in range(len(errorNodeList1) - 1):
                            if errorNodeList1[i] == n_missing:
                                nodesDelete.append(n_missing)
        self.nodestoDelete = nodesDelete                                            
        self.linkstocheck=array0
        
    def getLinkstoCheck(self):
        return self.linkstocheck

    def getNodestoDelete(self):
        return self.nodestoDelete
    
########################################################    
## Section 2.3: Read the transfer file that adds fixed routes back
    # Key words to locate to the correct table
word3='$+LINEROUTEITEM'   #Start
word4='$+TIMEPROFILE' #end
class RouteNodes:
    def __init__(self):
        self.routeNumber = 0

    def ReadRouteFile(self,errorNodeList_Class,NodeStopArray_Class):
        with open(routeAddedTransferFileStart, 'r') as fp:
            lines = fp.readlines()
            counter1=-1 
            startLineIndex=0
            endLineIndex=0
            nodeNumber=99
            currentRoute='0 '
            counter2=-1 #[node,stop] count
            for line in lines:
                if line.find(word4) != -1:
                    endLineIndex=1
                if startLineIndex>0 and endLineIndex!=1:  # means we are reading the rows in  Table: Line route items (inserted)
                    TrueLine = 0
                    if line.find('B;') !=-1:
                        TrueLine +=1
                        NodeStop=line.split(';')[3:5] #read the [node, stop] list, one of node orstop number is empty
                        counter2+=1
                        NodeStopArray_Class.getNodeStop(counter2,NodeStop,currentRoute)
                        nodeNum=line.split(';')[3] #read node number
                        currentRoute = line.split(';')[1]
                        if TrueLine == 1:
                            lastRoute = line.split(';')[1]
                        if nodeNum.isdigit() and currentRoute == lastRoute:
                            nodeNumber=nodeNum
                            counter1+=1
                        lastRoute = currentRoute
                    if nodeNumber != 99:
                        errorNodeList_Class.getErrorNodes(counter1,nodeNumber,currentRoute) #giving counter and node1 to the errorNodeList_Class
                if line.find(word3) != -1:
                    startLineIndex=1
          
########################################################               
## Section 2.4: Read the array of Nodes and Stops along the problematic route(s)
class ErrorNodeStopArray:
    def __init__(self):
        self.getNodeStopArray=[[0 for col in range(2)] for row in range(10000)]
        self.routeName2=[0]*10000
        self.counter=0
        self.fromStop =0
        self.toStop=0
        
    def getNodeStop(self,counter,NodeStop,thisRoute):
        self.getNodeStopArray[counter]= NodeStop
        self.routeName2[counter]= thisRoute
        self.counter=counter
        
    def getNodesStopCount(self):
        return self.counter
    
    def getFromStop(self):
        self.fromStop=self.getNodeStopArray[0][1]
        return self.fromStop
    
    def getToStop(self):
        self.toStop=self.getNodeStopArray[-1][1]
        return self.toStop
    
    def getRoute(self):
        return self.routeName2

########################################################  
## Section 2.5: Read the list of nodes along the problematic route(s)
class ErrorNodeList:
    def __init__(self):
        self.node1=[0]*10000
        self.node2=[0]*10000
        self.routeName=[0]*10000
        self.counter=0
        self.currentRoute=['0 ']*10000
        
    def getErrorNodes(self,counter,node1,currentRoute):
        self.node1[counter]= node1
        self.counter=counter
        self.currentRoute[counter]=currentRoute
        
    def checkNode1(self):
        return self.node1
    
    def errorNumNodes(self):
        return self.counter #numOfNodes
    
    def errorRouteID(self):
        return self.currentRoute

########################################################  
## Section 2.6: the list of error routes
class ErrorRouteList:
    def __init__(self):
        self.routeNum=[0]*100
        self.routeDir=[0]*100 
        self.routeDirection=[0]*100
        self.routeNameCheck=0
        self.counting1=0
        
    def getErrorRoute(self,counterRoute,routeNum,routeDir,routeDirection):
        if counterRoute==0:
            self.counting1=0
            self.routeNum[self.counting1]= routeNum
            self.routeDir[self.counting1]= routeDir  
            self.routeDirection[self.counting1]=routeDirection
            self.routeNameCheck=routeNum+routeDirection
            
        if self.routeNameCheck!=routeNum+routeDirection:
            self.counting1+=1
            self.routeNum[self.counting1]= routeNum
            self.routeDir[self.counting1]= routeDir  
            self.routeDirection[self.counting1]=routeDirection
            self.routeNameCheck=routeNum+routeDirection

    def ErrorRoute(self):
        return self.routeNum
    
    def ErrorDir(self):
        return self.routeDir
    
    def ErrorDirection(self):
        return self.routeDirection
    
    def ErrorLineDirection(self):
        return self.lineDirection
    
    def ErrorRouteCount(self):
        self.counting2=self.counting1+1
        return self.counting2

########################################################  
## Section 2.7: check if Node1, Node2 and the link in between is perfectly fine
class checkNode12ok():
    def getErrorNodes2(self,counter,node11,node21,routeThisNode,routeNextNode,NodesCheck,NodesTypeCheck): 
        self.checkNode1=[] #chekNodee1 is a list of Nodes that link to Node11 while Node21 has not been found to be linked to Node11
        self.checkNode2=[] # Nodes checkNode2 is a list of Nodes that link to Node21. checkNode2 would be empty if a link between Node11 & Node21 is found
        self.node11 = str(node11.strip()) #'10032516'
        self.node21 = str(node21.strip()) #'10040442'
        self.routeThisNode = routeThisNode
        self.routeNextNode = routeNextNode
        self.node12ok=999    # 
        with open(networkFileNameShort, 'r') as fp:
            lines = fp.readlines()
            node12ok=0
            for line in lines:
                # check if node1 is present on a current line: if it's in, it will be added to checkNode1
                if routeThisNode == routeNextNode:#otherwise there is no need to search a path between node 1 and 2                             
                    if line.find(';B') !=-1: #check links with Bus system
                        if line.split(';')[1]==node11 and line.split(';')[2]==node21:# when there's a link in the current network between two neighbour nodes along a line route
                            if ( (node11, node21) in NodesCheck) == False:
                                node12ok=1
                            else:
                                typeError= NodesTypeCheck[NodesCheck.index((node11, node21))][2]
                            
                                if typeError ==  'Link Close':
                                    node12ok = 4
                                    print("Link Close:", node12ok ) 
                                elif typeError == 'Turn block':
                                    node12ok==5
                                    print("Turn block:", node12ok) 
                                else:
                                    node12ok = -1
                                    print("Link exists but unknow Error between", node12ok) 
        self.counter = counter
        self.node12ok=node12ok
        #logging.debug(f'Initialiased checkNode12ok with counter: {self.counter}, node11: {self.node11}, node21: {self.node21}')
        if self.node12ok==999:
            print("No Link between ", node12ok)
        return self.node12ok     

########################################################  
## Section 2.8: Fix bus route in the transfer file
class FixBusRoute():
    def fixRoutes(self,nodesRemovalList,chains,fRead,fWrite):
        self.searchChains=chains
        self.fileRead=fRead
        self.fileWrite=fWrite
        with open(self.fileWrite, 'w') as fw, open(self.fileRead, 'r') as fp:
            lines = fp.readlines()
            inside_block = False
            new_lines = []            
            #loop over the lines
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                # Start checking between 'begin' and 'end'
                if word3 in line:
                    inside_block = True
                elif word4 in line:
                    inside_block = False
                new_lines.append(line)  # Add the line to the new_lines                
                # If we're inside the block, search for the patterns from searchChains
                if inside_block and i < len(lines) - 1:
                    next_line = lines[i+1].strip()
                    for i in range(len(nodesRemovalList)):
                        if nodesRemovalList[i] in line:
                            pass
                    # Iterate over each sublist in searchChains
                    for list_i in self.searchChains:
                        first, second, *middle, last = list_i
                        m = len(middle)  # The number of items between second and last                        
                        # Check the condition for the first and second items in line 'n'
                        # and first and last items in line 'n+1'
                        if (str(first) in line) and (str(second) in line) and (str(first) in next_line) and (str(last) in next_line):
                            # Add the original next line to new_lines
                            new_lines.append(next_line)                           
                            # Copy the line 'n+1' and paste m lines below
                            for j in range(m):
                                # Replace the second item with the middle items (3rd, 4th,...)
                                new_line = next_line.replace(str(last), str(middle[j]))
                                new_lines.append(new_line)                           
                            i += 1  # Skip the next line since it's already processed
                
                i += 1  # Move to the next line
           
            # Write all the new lines to the new file
            for line in new_lines:
                fw.write(line + '\n') 
            
        fw.close()
        fp.close()            
            
     
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
Visum = win32com.client.gencache.EnsureDispatch('Visum.Visum.24')
#Visum = win32com.client.Dispatch("Visum.Visum.24")
print("PTV Visum is started " +  str(Visum))
C = win32com.client.constants
thisProject=Visum.ScenarioManagement.OpenProject(scenarioManagementFile)
workingScenarioVersion=Visum.ScenarioManagement.CurrentProject.Scenarios.ItemByKey(workingScenarioId)# scenario with correct network check if it's 3 or 2
workingScenarioVersion.LoadInput() #this command loads network of succesful scenario
Visum.SaveVersion(workingScenarioName) #save .ver file to (workingScenarioName, with the file's location specified in the beginning
    
    #Create the latest *.net file with error (last scenario before error)
errorScenario=Visum.ScenarioManagement.CurrentProject.Scenarios.ItemByKey(errorScenarioId) #last scenario could be user input
errorScenario.LoadInput() #this command Loads the input version file (base version and all modifications) for this scenario into the running Visum
Visum.IO.SaveNet(networkFileName, LayoutFile='', EditableOnly=True, NonDefaultOnly=True, ActiveNetElemsOnly=False, NonEmptyTablesOnly=True) 
Visum.SetErrorFile(errorMessageLog)#writing error message on a defined file
#errorScenario.LoadInput()

########################################################
## Section 3.2: Define objectives through Classes
errorNodeClass=ErrorNodes() # read error message
nodeCheckList_Class=NodeCheckList()
errorRouteListClass=ErrorRouteList() # the list of error routes
errorNodeClass.ReadErrorFile(errorRouteListClass,nodeCheckList_Class) # GET ERROR ROUTE: call errorRouteListClass.getErrorRoute method, in which calls errorRouteList_Class.getErrorRoute(counter1,busRouteNumber,busRouteDir,direction)
errorRouteList=errorRouteListClass.ErrorRoute() #Return routeNum 
errorDirList=errorRouteListClass.ErrorDir()
errorDirectionList=errorRouteListClass.ErrorDirection()

errorNodesChecklist=nodeCheckList_Class.getcheckNode1() #list of all the nodes to check
errorNodesChecklist2=nodeCheckList_Class.getcheckNode2()
errorNodeTypeChecklist=nodeCheckList_Class.getErrorType() # list of 
errorNodesCheck= [(errorNodesChecklist[i],errorNodesChecklist2[i]) for i in range(len(errorNodesChecklist))]
errorNodesTypeCheck= [(errorNodesChecklist[i],errorNodesChecklist2[i], errorNodeTypeChecklist[i]) for i in range(len(errorNodesChecklist))]
print(f'Nodes to check and error types: {errorNodesTypeCheck}')

node12okClass=checkNode12ok()
fixBusRouteClass=FixBusRoute()

numOfRoutes=errorRouteListClass.ErrorRouteCount()
errorRoute=errorRouteList[1]
print(f"Number of Routes: {numOfRoutes}")

#############################################################################
#############################################################################
###### SECTION 4: FIX ROUTE ERRORS
########################################################

    # STEP 1 Load the working scenario to delete erroneous routes and create transfer files (1.deleted and 2.added)
    # routeDeletedTransferFile will be used as a new Modification
    # routeAddedTransferFileStart is where the routes will be fixed and then applied to the problematic 
Visum.LoadVersion(workingScenarioName) #load previously exported .ver file

for routeCount in range(numOfRoutes):  
    errorRoute=errorRouteList[routeCount]
    errorDir=errorDirList[routeCount]
    errorDirection=errorDirectionList[routeCount]

    errorRouteName=str(errorRoute)+" "+errorDir
    #errorRouteName=str(errorRouteName.strip())
    print("Error Route:")
    print(errorRoute,errorDir,errorDirection,errorRouteName)

    #2b Delete the Route in error file and save version
    RouteDelete=Visum.Net.LineRoutes.ItemByKey(errorRoute,errorDirection,errorRouteName)
    Visum.Net.RemoveLineRoute(RouteDelete)

Visum.SaveVersion(workingScenarioDeleteRoutesName)

    #2c	Create a transfer file *.tra file from b to a (destination)
Visum.GenerateModelTransferFileBetweenVersionFiles(workingScenarioDeleteRoutesName,workingScenarioName, routeAddedTransferFileStart, LayoutFile='', NonDefaultOnly=False, NonEmptyTablesOnly=True, WriteLayoutIntoModelTransferFile=True)
Visum.GenerateModelTransferFileBetweenVersionFiles(workingScenarioName,workingScenarioDeleteRoutesName, routeDeletedTransferFile, LayoutFile='', NonDefaultOnly=False, NonEmptyTablesOnly=True, WriteLayoutIntoModelTransferFile=True)


    # Create a new modification to delete the routes
newModification1 = thisProject.AddModification()
newModification1.SetAttValue("Code","Erroneous Routes Deleted")
newModification1.SetAttValue("Description","Copied from the last working modification and have problematic routes deleted")
newModNo1 = int(newModification1.AttValue("No"))
thisModName1=newModification1.AttValue("TraFile")

modFileName1="C:\\Users\\Shanshan Xie\\TfL\\06 Scenario management\\SM_TESTING\\Modifications\\"+thisModName1
shutil.copy2(routeDeletedTransferFile, modFileName1) #copy the transper file to the path of the scenario management's Modification folder

#Visum.SaveVersion(workingScenarioRoutesFixedName)

################################################
### Fix the routes in the transfer file (routeAddedTransferFileStart)
routeNodeClass=RouteNodes() #read from routeAddedTransferFileStart
errorNodeListClass=ErrorNodeList() 
#errorNodeStopArray=ErrorNodeStopArray()
errorNodeStopArrayClass=ErrorNodeStopArray()
routeNodeClass.ReadRouteFile(errorNodeListClass,errorNodeStopArrayClass) #get the list of odes and the nestedlist of nodes and stops / WITH OPEN(routeTransferFileStartName), WHICH IS A TRANSFER FILE THAT ADDS THE PROBLEM ROUTES
errorNodeStopArray = errorNodeStopArrayClass.getNodeStopArray #errorNodeStopArray is a nested list
numOfNodeStop = errorNodeStopArrayClass.getNodesStopCount()
errorRouteListLong=errorNodeStopArrayClass.getRoute()
#for i in range(len(errorRouteListLong)):
   # errorNodeStopArray[i][3] =errorRouteListLong[i]
errorNodeList1=errorNodeListClass.checkNode1()
errorRouteList=errorNodeListClass.errorRouteID()

numOfNodes=errorNodeListClass.errorNumNodes()
print(f"Number of nodes along the route(s): {numOfNodes}")

    # reduce the length of .net for speeding up
start_marker = "$LINK:NO"
end_marker = "$LINKPOLY"
with open(networkFileName, 'r') as fp:    
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
with open(networkFileNameShort, 'w') as output:
        output.writelines(result_lines)                

countingNode=0
nodelinks=[]

    # ! The pairs of nodes recognised through "for count in range(numOfNodes-1)" iretation are all successive nodes along the original route
for count in range(numOfNodes-1):
    print('Checkng Count:', count)
    checkNode1=errorNodeList1[count]
    checkNode2=errorNodeList1[count+1]
    checkRouteThisNode=errorRouteList[count]
    checkRouteNextNode=errorRouteList[count+1]    
    node12ok=node12okClass.getErrorNodes2(count,checkNode1,checkNode2,checkRouteThisNode,checkRouteNextNode,errorNodesCheck,errorNodesTypeCheck) #return 999 or 1 or the missing node that can be solved by Birendra's method
        ######
        #node12ok=1: node 1, 2 and the link, turn... from node1 to 2 are fine
        #node12ok=2: node 1 exists, node 2 doesn't exist, which will also leads to 'no link warning'
        #node12ok=3: node 1, 2 exist, but no link from 1 to 2 
        #node12ok=4: node 1, 2 exist, but Link close
        #node12ok=5: node 1, 2 and the link from 1 to 2 exist, but there are turn, lane, ... issues.
        ######      
    nodelinks.append([checkNode1,checkNode2,node12ok])

##### Problematic nodes read from the modification file (.tra)
    # ! The pairs of nodes recognised from the modification 
modificationCheck=ModificationCheckList()
modificationCheck.setLinkstoCheck(errorModification)
nodelinksReplace = modificationCheck.getLinkstoCheck()
nodelinksReplace = [[str(x), str(y), z] for x, y, z in nodelinksReplace]
for i1 in range(len(nodelinksReplace)):
    for i2 in range(len(nodelinks)):
        if nodelinksReplace[i1][0]==nodelinks[i2][0] and nodelinksReplace[i1][1]==nodelinks[i2][1]:
            nodelinks[i2][2]=nodelinksReplace[i1][2]
    # Create a new .ver for shortest path search (where problematic routes have been deleted)    

Visum2 = win32com.client.gencache.EnsureDispatch('Visum.Visum')
Visum2.LoadVersion(workingScenarioDeleteRoutesName)
Visum2.ApplyModelTransferFile(errorModification)

Visum2.IO.LoadNet(networkFileName, ReadAdditive=False, RouteSearch=None, AddNetRead=None, NormalizePolygons=True, MergeSameCoordPolygonPoints=True, DecimalsForMergeSameCoordPolygonPoints=-1)

# Messages in the widget
all_messages = ""

# Initialise variables to track state
n_found = False
a_n = None
searchChains=[] #the list of lists of nodes needing to be added to the route
for i in range(len(nodelinks)):
    # route_i = checkRouteThisNode[i]
    # Check if the third column is not equal to 1
    if nodelinks[i][2] != 1 and not n_found:
        a_n = nodelinks[i][0]  # Capture the first column value as a_n
        n_found = True  # We found a_n, now we search for a_m
    
    # Now we search for the row where the third column equals 1
    if nodelinks[i][2] == 1 and n_found:
        a_m = nodelinks[i][0]  # Capture the first column value as a_m
        #seachNode1n2.append((a_n, a_m))  # Append the tuple (a_n, a_m) to array1
        try:
            aNetElementContainer = Visum2.CreateNetElements()
            node1 = Visum2.Net.Nodes.ItemByKey(int(a_n))
            node2 = Visum2.Net.Nodes.ItemByKey(int(a_m))
            aNetElementContainer.Add(node1)
            aNetElementContainer.Add(node2)
            #Visum2.Net.Links.AddUserDefinedAttribute('ShortestPath','ShortestPath','ShortestPath',1)
            Visum2.Analysis.RouteSearchPrT.Execute(aNetElementContainer,'T',0, IndexAttribute='SPath')
            #####! remember to clear after each seach
            NodeChainPuT=Visum2.Analysis.RouteSearchPuTSys.NodeChainPuT
            NodeChain=Visum2.Analysis.RouteSearchPrT.NodeChainPrT
            chain=[errorRouteList[i]]
            for n in range(len(NodeChain)):
                chain.append(NodeChain[n].AttValue("NO"))
            #Visum2.Analysis.RouteSearchPuTSys.Clear() 
            if chain!=[errorRouteList[i]]: #the first item being the route
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
all_messages += 'Dear Modeller: the following routes have been rerouted through shortest path. Please review the routes and make necessary changes'
# Can print out more info. like between Node ? and Node ?
for i1 in range(len(searchChains)):
    print('Route ', searchChains[i1][0], ': please review the route between ', searchChains[i1][1], 'and ', searchChains[i1][-1])
    message = f"Route {searchChains[i1][0]}: please review the route between {searchChains[i1][1]} and {searchChains[i1][-1]}"
nodesDeleteList = modificationCheck.getNodestoDelete()
if searchChains != []:
    shutil.copy2(routeAddedTransferFileStart, routeTransferFileTempName) #to keep the start file unchanged
    fixBusRouteClass.fixRoutes(nodesDeleteList,searchChains,routeTransferFileTempName,routeAddedTransferFileFinal)
    
    
Visum3 = win32com.client.gencache.EnsureDispatch('Visum.Visum')
Visum3.LoadVersion(workingScenarioDeleteRoutesName)
# create AddNetRead-Object and specify desired conflict avoiding method
anrController = Visum3.IO.CreateAddNetReadController()
anrController.SetWhatToDo("Line",C.AddNetRead_OverWrite)
anrController.SetWhatToDo("LineRoute", C.AddNetRead_Ignore)
anrController.SetWhatToDo("LineRouteItem",C.AddNetRead_Ignore)
anrController.SetWhatToDo("TimeProfile", C.AddNetRead_Ignore)
anrController.SetWhatToDo("TimeProfileItem", C.AddNetRead_Ignore)
anrController.SetWhatToDo("VehJourney", C.AddNetRead_Ignore)
anrController.SetUseNumericOffset("VehJourney", True)
anrController.SetWhatToDo("VehJourneyItem",C.AddNetRead_DoNothing)
anrController.SetWhatToDo("VehJourneySection", C.AddNetRead_Ignore)
anrController.SetWhatToDo("ChainedUpVehJourneySection", C.AddNetRead_DoNothing)
anrController.SetWhatToDo("UserAttDef", C.AddNetRead_Ignore)
anrController.SetWhatToDo("Operator", C.AddNetRead_OverWrite)

anrController.SetConflictAvoidingForAll(10000,"ORG_")
# apply a model transfer
Visum3.ApplyModelTransferFile(errorModification,anrController)
Visum3.SaveVersion(workingScenarioLoadErrorMod)
Visum3.GenerateModelTransferFileBetweenVersionFiles(workingScenarioDeleteRoutesName,workingScenarioLoadErrorMod, errorModTransferFile, LayoutFile='', NonDefaultOnly=False, NonEmptyTablesOnly=True, WriteLayoutIntoModelTransferFile=True)


Visum3.ApplyModelTransferFile(routeAddedTransferFileFinal,anrController)
Visum3.SaveVersion(workingScenarioRoutesFixedName)
Visum3.GenerateModelTransferFileBetweenVersionFiles(workingScenarioLoadErrorMod,workingScenarioRoutesFixedName, routesFixedTransferFile, LayoutFile='', NonDefaultOnly=False, NonEmptyTablesOnly=True, WriteLayoutIntoModelTransferFile=True)


### copying final transfer files to mod files
# new errorModification
newModification = thisProject.AddModification()
newModification.SetAttValue("Code","Refined Problematic Modification")
newModification.SetAttValue("Description","Copied from the modification with error, with the erroreous modiffication reloaded using conflict avoiding parameters")
newModNo2 = int(newModification.AttValue("No"))
thisModName2=newModification.AttValue("TraFile")
modFileName2="C:\\Users\\Shanshan Xie\\TfL\\06 Scenario management\\SM_TESTING\\Modifications\\"+thisModName2
shutil.copy2(errorModTransferFile, modFileName2) #to keep the start file unchanged

#add the fixed routes
newModification = thisProject.AddModification()
newModification.SetAttValue("Code","Problematic Routes Re-added")
newModification.SetAttValue("Description","Have the deleted problematic routes added")
newModNo3 = int(newModification.AttValue("No"))
thisModName3=newModification.AttValue("TraFile")

modFileName3="C:\\Users\\Shanshan Xie\\TfL\\06 Scenario management\\SM_TESTING\\Modifications\\"+thisModName3
shutil.copy2(routeAddedTransferFileFinal, modFileName3) #to keep the start file unchanged

###### apply the Modification with error

oldModSet=errorScenario.AttValue("MODIFICATIONS")
print(oldModSet)
#####################################################################################
# !
# ??
#TO-DO: check below
#####BELOW: The last Mod which leads to bus route error need to be deleted
newModSet=oldModSet[:-1]+str(newModNo1)+","+str(newModNo2)+","+str(newModNo3)
#
print(newModSet)
#curScenario=thisProject.Scenarios.ItemByKey(8)
curScenario=thisProject.AddScenario()
curScenarioNumber=curScenario.AttValue("NO")
curScenario.SetAttValue("CODE","BusRouteFixed")
curScenario.SetAttValue("PARAMETERSET","1")
#curScenario.SetAttValue("MODIFICATIONS","1,2,3,5,7,11")##11 should be from new mod file and others from user input scenario
curScenario.SetAttValue("MODIFICATIONS",newModSet)
#errorMessageFile=errorMessageDir+str(errorScenarioId)+".txt"
errorMessageFile1=errorMessageDir+str(curScenarioNumber)+".txt"#new error file
Visum.SetErrorFile(errorMessageFile1)#writing error message on a defined file
curScenario.LoadInput()

# show warning
#root = tk.Tk()
#root.withdraw()  # Hide the main window
#messagebox.showwarning('Dear Modeller: the following routes have been rerouted through shortest path. Please review the routes and make necessary changes:')
#root.quit()
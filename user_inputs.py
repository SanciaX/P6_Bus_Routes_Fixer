"""
user_inputs.py
"""


from pathlib import Path

# SECTION 1: User Input
errorScenarioId = 8  # Scenario with bus route issues
workingScenarioId = 2  # Last scenario without network errors
errorModificationID = 2  # First modification where the route errors occur

# Scenario management paths and files
scenarioManagementFile = r"C:\\Users\\Shanshan Xie\\TfL\\06 Scenario management\\SM_TESTING\\SM_TESTING.vpdbx"
scenarioManagementPath = r"C:\\Users\\Shanshan Xie\\TfL\\06 Scenario management\\SM_TESTING"
busRoutesFixPath = r"C:\\Users\\Shanshan Xie\\TfL\\06 Scenario management\\Bus_Routes_Fix"  # Temp folder for bus route fixes

## Section 1.2 Define files
# Error modification file in SM_TESTING folder
errorModificationList = list(scenarioManagementPath + r'\Modifications\M000000.tra')
errorModificationList[-len(str(errorModificationID)) - 4] = str(errorModificationID)
errorModification = ''.join(errorModificationList)

# Find the error messages in the SM_TESTING folder
errorMessageDir = scenarioManagementPath + r'\Scenarios\S000008'  # Dir of the error messages
errorMessageFile = errorMessageDir + r'\Messages.txt'
# Message log
errorMessageLog = busRoutesFixPath + r'\MessageLog.txt'


# .ver files
workingScenarioName = busRoutesFixPath + r'\scenarioWorking.ver'

workingScenarioDeleteRoutesName = busRoutesFixPath + r'\scenarioWorkingDeleteRoutes.ver'

workingScenarioLoadErrorMod = busRoutesFixPath + r'\workingScenarioLoadErrorMod.ver'

workingScenarioRoutesFixedName = busRoutesFixPath + r'\scenarioWorkingRoutesFixed.ver'

RouteSearchVersion = busRoutesFixPath + r'\RouteSearchVersion.ver'


# .net files
networkFileName = busRoutesFixPath + r'\NetworkFileError.net'

networkFileNameShort = busRoutesFixPath + r'\NetworkFileErrorShort.net'


# .tra files
routeDeletedTransferFile = busRoutesFixPath + r'\routeDeletedTransfer.tra'

routeAddedTransferFileStart = busRoutesFixPath + r'\routeTransferFileStart.tra'

routeTransferFileTempName = busRoutesFixPath + r'\routeTransferFileTemp.tra'

routeAddedTransferFileFinal = busRoutesFixPath + r'\routeTransferFileFinal.tra'

routesFixedTransferFile = busRoutesFixPath + r'\routeFixedTransferFile.tra'

errorModTransferFile = busRoutesFixPath + r'\errorModTransferFile.tra'

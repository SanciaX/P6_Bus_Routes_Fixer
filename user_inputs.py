"""
user_inputs.py
"""


from pathlib import Path

# SECTION 1: User Input
error_scenario_id = 8  # Scenario with bus route issues
working_scenario_id = 2  # Last scenario without network errors
error_modification_id = 2  # First modification where the route errors occur

# Scenario management paths and files
scenario_management_file = r"C:\\Users\\Shanshan Xie\\TfL\\06 Scenario management\\SM_TESTING\\SM_TESTING.vpdbx"
scenario_management_path = r"C:\\Users\\Shanshan Xie\\TfL\\06 Scenario management\\SM_TESTING"
bus_routes_fix_path = r"C:\\Users\\Shanshan Xie\\TfL\\06 Scenario management\\Bus_Routes_Fix"  # Temp folder for bus route fixes

## Section 1.2 Define files
# Error modification file in SM_TESTING folder
error_modification_list = list(scenario_management_path + r'\Modifications\M000000.tra')
error_modification_list[-len(str(error_modification_id)) - 4] = str(error_modification_id)
error_modification = ''.join(error_modification_list)

# Find the error messages in the SM_TESTING folder
error_message_dir = scenario_management_path + r'\Scenarios\S000008'  # Dir of the error messages
error_message_file = error_message_dir + r'\Messages.txt'
# Message log
error_message_log = bus_routes_fix_path + r'\MessageLog.txt'


# .ver files
working_scenario_name = bus_routes_fix_path + r'\scenarioWorking.ver'

working_scenario_delete_routes_name = bus_routes_fix_path + r'\scenarioWorkingDeleteRoutes.ver'

working_scenario_load_error_mod = bus_routes_fix_path + r'\working_scenario_load_error_mod.ver'

working_scenario_routes_fixed_name = bus_routes_fix_path + r'\scenarioWorkingRoutesFixed.ver'

route_search_model = bus_routes_fix_path + r'\route_search_model.ver'


# .net files
network_file_name = bus_routes_fix_path + r'\NetworkFileError.net'

network_file_name_short = bus_routes_fix_path + r'\NetworkFileErrorShort.net'


# .tra files
route_deleted_transfer_file = bus_routes_fix_path + r'\routeDeletedTransfer.tra'

route_added_transfer_file_start = bus_routes_fix_path + r'\routeTransferFileStart.tra'

route_transfer_file_temp_name = bus_routes_fix_path + r'\routeTransferFileTemp.tra'

route_added_transfer_file_final = bus_routes_fix_path + r'\routeTransferFileFinal.tra'

routes_fixed_transfer_file = bus_routes_fix_path + r'\routeFixedTransferFile.tra'

error_mod_transfer_file = bus_routes_fix_path + r'\error_mod_transfer_file.tra'

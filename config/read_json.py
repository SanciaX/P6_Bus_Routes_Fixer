import os
import json
from pathlib import Path

# Get the current working directory
current_path = Path(os.getcwd())
print(f"The current working directory is: {current_path}")

# Construct the path to the directories.json file
json_file_path = current_path /'config' / 'directories.json'
print(f"The JSON file path is: {json_file_path}")

# Load the JSON file
print(f"Does the JSON file exist? {json_file_path.exists()}")
with open(json_file_path, 'r') as file:
    directories = json.load(file)

print(directories)

# Define base paths
bus_routes_fix_path = current_path / directories['base_path']
scenario_management_path = Path(directories['scenario_management_path'])
modifications_path = scenario_management_path / directories['modifications_path']
scenarios_path = scenario_management_path / directories['scenarios_path']

# Define IDs
error_scenario_id = directories['error_scenario_id']
# working_scenario_id = directories['working_scenario_id']
error_modification_id = directories['error_modification_id']

# Define files using relative paths
scenario_management_file = scenario_management_path / 'Bus_Route_Script_Test_Subnetwork.vpdbx'
error_modification_list = list(str(modifications_path / 'M000000.tra'))
error_modification_list[-len(str(error_modification_id))-4 :-4] = str(error_modification_id) # error_modification_id can have 1,.2, 3,... digital
error_modification = ''.join(error_modification_list)

 #error_message_path = scenarios_path / 'S000001'
error_scenario_id_str = 'S000'+ str(error_scenario_id)
error_message_path = scenarios_path / error_scenario_id_str
error_message_file = error_message_path / 'Messages.txt'
error_message_log = bus_routes_fix_path / 'MessageLog.txt'

working_scenario_name = bus_routes_fix_path / 'scenarioWorking.ver'
working_scenario_delete_routes_name = bus_routes_fix_path / 'scenarioWorkingDeleteRoutes.ver'
working_scenario_load_error_mod = bus_routes_fix_path / 'working_scenario_load_error_mod.ver'
working_scenario_routes_fixed_name = bus_routes_fix_path / 'scenarioWorkingRoutesFixed.ver'
route_search_version = bus_routes_fix_path / 'route_search_model.ver'

error_scenario_network_file_name = bus_routes_fix_path / 'NetworkFileError.net'
network_file_table_of_links = bus_routes_fix_path / 'NetworkFileErrorLinks.net'
network_file_table_of_turns = bus_routes_fix_path / 'NetworkFileErrorTurns.net'

route_deleted_transfer_file = bus_routes_fix_path / 'routeDeletedTransfer.tra'
route_added_transfer_file_start = bus_routes_fix_path / 'routeAddedTransferStart.tra'
route_added_transfer_file_temp = bus_routes_fix_path / 'routeAddedTransferTemp.tra'
route_added_transfer_file_final = bus_routes_fix_path / 'routeAddedTransferFileFinal.tra'
routes_fixed_transfer_file = bus_routes_fix_path / 'routeFixedTransferFile.tra'
error_mod_transfer_file = bus_routes_fix_path / 'error_mod_transfer_file.tra'
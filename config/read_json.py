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
scenario_management_file = scenario_management_path / 'SM_TESTING.vpdbx'
error_modification_list = list(str(modifications_path / 'M000000.tra'))
error_modification_list[-len(str(error_modification_id)) - 4] = str(error_modification_id) # error_modification_id can have 1,.2, 3,... digital
error_modification = ''.join(error_modification_list)

error_message_dir = scenarios_path / 'S000008'
error_message_file = error_message_dir / 'Messages.txt'
error_message_log = bus_routes_fix_path / 'MessageLog.txt'

working_scenario_name = bus_routes_fix_path / 'scenarioWorking.ver'
working_scenario_delete_routes_name = bus_routes_fix_path / 'scenarioWorkingDeleteRoutes.ver'
working_scenario_load_error_mod = bus_routes_fix_path / 'working_scenario_load_error_mod.ver'
working_scenario_routes_fixed_name = bus_routes_fix_path / 'scenarioWorkingRoutesFixed.ver'
route_search_version = bus_routes_fix_path / 'route_search_model.ver'

network_file_name = bus_routes_fix_path / 'NetworkFileError.net'
network_file_name_short = bus_routes_fix_path / 'NetworkFileErrorShort.net'

route_deleted_transfer_file = bus_routes_fix_path / 'routeDeletedTransfer.tra'
route_added_transfer_file_start = bus_routes_fix_path / 'routeTransferFileStart.tra'
route_transfer_file_temp_name = bus_routes_fix_path / 'routeTransferFileTemp.tra'
route_added_transfer_file_final = bus_routes_fix_path / 'routeTransferFileFinal.tra'
routes_fixed_transfer_file = bus_routes_fix_path / 'routeFixedTransferFile.tra'
error_mod_transfer_file = bus_routes_fix_path / 'error_mod_transfer_file.tra'
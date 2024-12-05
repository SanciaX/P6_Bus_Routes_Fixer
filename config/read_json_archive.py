import json
import os

# Load the configuration JSON file
with open("directories.json", "r") as config_file:
    config = json.load(config_file)

# Base directory
base_dir = config["base_dir"]

# Define paths for scenario management and bus routes fix based on the JSON file
scenario_management_path = os.path.join(base_dir, config["folders"]["sm_testing"])
bus_routes_fix_path = os.path.join(base_dir, config["folders"]["bus_routes_fix"])

# Paths to specific files
scenario_management_file = os.path.join(base_dir, config["files"]["scenario_management_file"])
error_message_file = os.path.join(base_dir, config["files"]["error_message_file"])
error_message_log = os.path.join(base_dir, config["files"]["error_message_log"])

# Example: Accessing version files
working_scenario_ver = os.path.join(base_dir, config["files"]["working_scenario_ver"])
working_scenario_delete_routes_ver = os.path.join(base_dir, config["files"]["working_scenario_delete_routes_ver"])
working_scenario_load_error_mod_ver = os.path.join(base_dir, config["files"]["working_scenario_load_error_mod_ver"])
working_scenario_routes_fixed_ver = os.path.join(base_dir, config["files"]["working_scenario_routes_fixed_ver"])
route_search_version_ver = os.path.join(base_dir, config["files"]["route_search_version_ver"])

# Example: Accessing .net files
network_file_error_net = os.path.join(base_dir, config["files"]["network_file_error_net"])
network_file_error_short_net = os.path.join(base_dir, config["files"]["network_file_error_short_net"])

# Example: Accessing .tra files
route_deleted_transfer_tra = os.path.join(base_dir, config["files"]["route_deleted_transfer_tra"])
route_transfer_file_start_tra = os.path.join(base_dir, config["files"]["route_transfer_file_start_tra"])
route_transfer_file_temp_tra = os.path.join(base_dir, config["files"]["route_transfer_file_temp_tra"])
route_transfer_file_final_tra = os.path.join(base_dir, config["files"]["route_transfer_file_final_tra"])
routes_fixed_transfer_file = os.path.join(base_dir, config["files"]["routes_fixed_transfer_file"])
error_mod_transfer_file = os.path.join(base_dir, config["files"]["error_mod_transfer_file"])

# Output the paths to verify
print("Scenario Management File Path:", scenario_management_file)
print("Error Message File Path:", error_message_file)
print("Error Message Log Path:", error_message_log)

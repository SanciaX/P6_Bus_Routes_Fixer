
"""
# -*- coding: utf-8 -*-
This version addresses various route error types through shortest-path search including 'turn closed', 'no link', ''is blocked for the transport system''
Author: Shanshan Xie, Adam Fradgley & Birendra Shrestha
Adapted from: P6FixBusRoute30.py (Birendra Shrestha)

Instructions:
- Step 1: Specify 'scenario_management_base_path', 'scenario_management_project_path' 'error_modification_id' & 'error_scenario_id' in the ../directories.json
- Step 2: Run the main script 'bus_routes_fixer.py'
"""


from source_code.bus_routes_fixer import main


if __name__ == "__main__":
    config_path = "config/directories.json"
    main(config_path)
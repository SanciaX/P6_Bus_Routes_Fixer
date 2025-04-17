
"""
# -*- coding: utf-8 -*-
This version addresses various route error types through shortest-path search including 'turn closed', 'no link', ''is blocked for the transport system''
Author: Shanshan Xie, Adam Fradgley & Birendra Shrestha
Adapted from: P6FixBusRoute30.py (Birendra Shrestha)

Instructions:
- Step 1: Specify 'scenario_management_temp_files_path', 'scenario_management_project_path' 'first_error_modification_id' & 'error_scenario_id' in the ../directories.json
- Step 2: Run the main script 'bus_routes_fixer.py'
"""

import cProfile
import pstats

from ..bus_routes_fixer import main

if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()

    config_path = "bus_routes_fixer/config/directories.json"
    main(config_path)

    profiler.disable()

    stats = pstats.Stats(profiler)
    stats.strip_dirs()  # Clean up file paths
    stats.sort_stats("time")  # Sort by time spent in each function
    stats.print_stats(50)  # Print the top 50 results
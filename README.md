# Fixing Bus Routes in Visum Scenario Management 

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/release)

This repository contains Python scripts designed to fix bus routes in Visum Scenario Management (PTV Visum 2024/2025).

---

## Features

### 1. Identify Erroneous Scenario and Prepare Data
- Locate the erroneous scenario in the Scenario Management Project.
- Identify the modification causing route errors.
- Copy the required files (`.net`, `.tra`, `.txt`) to facilitate fixing.

### 2. Build a Working Scenario and Create Transfer Files
- Create a new scenario (`working_scenario`) with all modifications up to the error-inducing modification (`Mods_(pre_error)`).
- Generate a transfer file (`.tra`) to delete problematic routes and apply it to a new modification (`Mod_(delete_routes)`).
- Compare models before and after the deletion to generate `routeAddedTransferStart.tra`, containing route-related data for restoring routes.
- Update `routeAddedTransferStart.tra` to `routeAddedTransferTemp.tra` by:
  - Adjusting bus route and profile data.
  - Removing problematic route entries from the error-causing modification (`Mod_error`).

### 3. Identify Link/Turn Errors Along Problematic Routes
- Extract nodes along problematic routes from `routeAddedTransferTemp.tra`.
- In the `Table: Links` and `Table: Turns` sections of the `.net` file, identify node pairs causing errors (e.g., missing links or restricted turns).

### 4. Apply Shortest Path Search in Visum
- Load the erroneous scenario’s `.net` file in Visum.
- Search for alternative paths between expanded node pairs (`node_(search_start)` to `node_(search_end)`) around problem areas.
- Replace problematic route segments with paths found by the shortest path search.
- Update time profile data and save as `routeAddedTransferFinal.tra`.

### 5. Generate the Fixed Scenario
- Create a new scenario with:
  - Modifications before the error (`Mods_(pre_error)`).
  - Route deletions (`Mod_(delete_routes)`).
  - The corrected error modification (`Mod_error`).
  - The updated transfer file (`routeAddedTransferFinal.tra`).

### 6. Notify the Modeller
- Display a message box indicating successfully found paths.
- Provide reminders to verify the modified scenario in Visum.

---
## Getting Started

- Clone the repository to your local machine.
- Install the required Python modules using `pip`.
- Check the ID of the scenario you'd like to fix in Visum. From the error message of this scenario, find the ID of the modification causing the error.
- Open the `config/directories.json` file and specify the path of your scenario management (scenario_management_path), the ID of the scenario with route error(s) (scenario_management_path), and the ID of the modification causing the error (error_modification_id).
- Run the `run_me.py` script (as Admin).

## Requirements

- Python 3.9 or later
- PTV Visum 2024/2025
- Your Scenario Management projects, or download the example model from [PCAM/P6 Tool/Example_Model_Scenario](https://transportforlondon.sharepoint.com/:f:/r/sites/one-pcam/Shared%20Documents/P6%20Tool/Eaxample%20Model_Scenario%20Management%20Bus%20Routes?csf=1&web=1&e=4ZptbN)

### Python Modules

Install the required Python modules using `pip`:

```bash
# create venv
cd \venvs\directory
python -m venv p6_fix_bus_routes

# activate venv
activate Scripts\activate.bat

# clone the repo
cd \git\repos\directory
git clone https://github.com/SanciaX/P6_Fix_Bus_Routes.git
cd P6_Fix_Bus_Routes

# install requirements
pip install -r requirements.txt

# run the main script
python bus_routes_fixer.py
```

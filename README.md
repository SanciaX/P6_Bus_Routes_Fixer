# Fixing Bus Routes in Visum Scenario Management 

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/release)

This repository contains Python scripts designed to fix bus routes in Visum Scenario Management (PTV Visum 2024/2025).

---

## Features

### 1. Identify Error Route(s) and Route Items, and Create a New Modification to Delete Error Routes
- Identify the modification causing errors
- Create a new scenario containing the modifications before the error occurs (`working_scenario`)
- Save route items along the error route(s) in the network before loading the error modification. (Note that there may be one or multiple erroneous routes.)
- Make a copy of the error scenario model (`scenarioError.ver`)  with error routes deleted
- Save the transfer file that deletes routes from the working scenario (`routeDeletedTransfer.tra`)
- Apply `routeDeletedTransfer.tra` to a new modification (`Modification Code: Delete Problematic Routes for Scenario xxx`) in Scenario Management


### 2. Add Back Deleted Routes with Non-existent Route Items Deleted and Incomplete Route Section Found through Shortest Path Search 
- Identify problematic links and turns along the error route(s) in the error scenario's network (using `Visum.Net.Links.LinkExistsByKey` and `Visum.Net.Turns.TurnExistsByKey`)
- For each error route, find the start and end nodes (`node_before_errors` and `node_after_errors` ) with errors in between.
- Find the last node before errors occur (`search_start`) and the first node after all the errors (`search_start`)
- Get the indices of these two nodes in the routeitems instance, so that later the routeitems in between will not be included when adding back new route in the next step 
- Add each deleted route back, using `Visum.Net.AddLineRoute` with WhatToDo parameters.
- Save the transfer file of adding fixed routes back (`fixedRouteAddedTransfer.tra`)

### 3. Create New Modifications to Add the Error Modification Back and Add the Fixed Routes Back; Create the Scenario with the Same Network as The Error Scenario but Fixed Error Route(s)
- Create a new scenario with:
  - Modifications before the error
  - Route deletions modification
  - The corrected error modification
  - A Modification that adds the fixed routes back

### 4. Notify the Modeller
- Display a message box indicating successfully found paths.
- Leave the log file for the modeller to check.

---
## Getting Started

- Clone the repository to your local machine.
- Install the required Python modules using `pip`.
- Check the ID of the scenario you`d like to fix in Visum. From the error message of this scenario, find the ID of the modification causing the error.
- Open the `config/directories.json` file and specify the ID of the scenario with route error(s) (scenario_management_path), the ID of the modification causing the error (error_modification_ids), the path of your scenario management (scenario_management_base_path) and the path of the scenario management file(.vpdbx) (scenario_management_project_path).
- Run the `bus_routes_fixer.py` script in the source_code folder (as Admin).

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
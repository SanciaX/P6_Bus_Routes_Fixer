# Fixing Bus Routes in Visum Scenario Management 

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/release)

This repository contains Python scripts designed to fix bus routes in Visum Scenario Management (PTV Visum 2024/2025). It is developed for the P6 ONE Model, which is an asset of Transport for London (TfL) Network Performance Modelling and Visualisation team. 

---

## Features

The tool is intended to be used when a Visum scenario contains modifications with conflicting bus routes, leading to assignment failures. The tool automates the process of identifying and fixing bus route related issues, ensuring that all the network changes, except some bus route changes, in these modifications are preserved while resolving route-related errors. 

---


## Requirements

- Python 3.9 or later
- PTV Visum 2024/2025
- Your Scenario Management projects, or download the example model from [PCAM/P6 Tool/Example_Model_Scenario](https://transportforlondon.sharepoint.com/:f:/r/sites/one-pcam/Shared%20Documents/P6%20Tool/Eaxample%20Model_Scenario%20Management%20Bus%20Routes?csf=1&web=1&e=4ZptbN)
---

## Getting Started

- Clone the repository to your local machine.
### Install with pip
```commandline
pip install git+https://github.com/SanciaX/P6_Bus_Routes_Fixer.git
```
### Install with git
```commandline
git clone https://github.com/SanciaX/P6_Bus_Routes_Fixer.git
pip install -r requirements.txt
```
- Configure the python environment for using the Bus_Routes_Fixer:
  - In a terminal, navigate to your project folder:
  ```commandline
  cd ..\Bus_routes_fixer 
  ```
  -  Run the environment setup script:
  ```commandline
  python setup_env.py 
  ```
  -  Activate the environment
    ```commandline
  .venv\Scripts\activate 
  ```
  
- Identify the ID of the scenario you want to fix in Visum. From the error message of this scenario, find the ID of the first modification causing the error.
- Open `../bus_routes_fixer/config/directories.json`, specify the values of the following variables: 

  1) ID of the scenario with route error(s) (error_scenario_id), identified in step 3; 

  2) ID of the first modification causing errors (id_of_the_1st_error_modification), identified in from the error message;

  3) Path of your scenario management (scenario_management_base_path); and  

  4) Path of the scenario management file(.vpdbx) (scenario_management_project_path). 

- Run your main script:
```commandline
python -m bus_routes_fixer.user_run_scripts.user_run
```
- Check `../bus_routes_fixer/outputs/bus_routes_screenshots` and `../bus_routes_fixer/outputs/log` for the paths of fixed bus routes and reroute them in the last modification if necessary.
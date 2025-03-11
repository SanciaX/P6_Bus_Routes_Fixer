"""
This module contains functions that help to identify error routes.
"""

import shutil
from visum_sm_functions import add_scenario, add_modification, apply_model_transfer, get_route_items

def read_scenario_management(visum, sm_project, config):
    """
    Create a new scenario containing the modifications before the error occurs and save the .ver file
    """
    error_scenario = visum.ScenarioManagement.CurrentProject.Scenarios.ItemByKey(config.error_scenario_id)
    old_mod_set = error_scenario.AttValue("MODIFICATIONS")
    mod_list = old_mod_set.split(',')
    working_scenario_modification_set = []
    stop = False
    for i in mod_list:
        if int(config.error_modification_id) == int(i):
            stop = True
        elif not stop:
            working_scenario_modification_set.append(i)
    working_mod_set = ','.join(working_scenario_modification_set)
    
    working_scenario = add_scenario(visum, sm_project, working_mod_set, config.scenarios_path,
                                    "Deselect the modification causing error")
    working_scenario.LoadInput()
    visum.SaveVersion(config.working_scenario_path)
    working_scenario.AttValue("NO")
    return working_scenario_modification_set

def save_error_routes(visum1, visum2, config):
    """
    Identify and remove erroneous routes which are recognised from the messages file.
    """
    visum2.LoadVersion(config.working_scenario_path) #visum2 links to error route instances
    visum1.LoadVersion(config.working_scenario_path) #visum controls the scenario management project
    error_routes_dict = {}
    error_iLineRoute_instances = []
    try:
        with open(config.error_message_path, "r") as fp:
            lines = fp.readlines()
    except FileNotFoundError:
        print("Error: Messages file not found.")
        return error_routes_dict, error_iLineRoute_instances

    for line in lines:
        if "Warning Line route" in line or "Error Line route" in line:
            try:
                first_semicolon = line.find(';')
                second_semicolon = line.find(';', first_semicolon + 1)
                route_name = line[first_semicolon + 1:second_semicolon]
                line_name = route_name[:route_name.find(' ')]
                direction_code = line[second_semicolon + 1:second_semicolon + 2]
                nodes, stops = get_route_items(route_name,visum2)
                if not route_name in error_routes_dict:
                    error_routes_dict[route_name] = {'nodes': nodes, 'stops': stops, 'direction_code': direction_code}
                # Save delete_routes.ver and add_routes.ver
                    iLineRoute_to_delete = visum2.Net.LineRoutes.ItemByKey(line_name, direction_code, route_name)
                    route_to_remove = visum1.Net.LineRoutes.ItemByKey(line_name, direction_code, route_name)
                    if iLineRoute_to_delete:
                        visum1.Net.RemoveLineRoute(route_to_remove)
            except Exception:
                continue
    return error_routes_dict

def save_fixed_error_modification(visum1, config):
    """
    Create fixedErrorModificationFile.tra, which is a copy of the error modification but with no info. about the error routes already deleted from the network.
    This is to avoid errors that may occur when loading the error modification if the original error modification .tra contains data about error routes that are already deleted
    """
        # Delete error routes from the network before loading the modification causing errors
    visum1.SaveVersion(config.working_scenario_delete_routes_path)
        # Apply the error modification with an anrController.SetWhatToDo parameter that ignore conflicting LineRouteItem data, so that when load ing the error modification, if the error modification contains data about routes just deleted, there wouldn't be error
    apply_model_transfer(visum1, config.error_modification)
        # Save the Error Scenario Model with the error routes deleted
    visum1.SaveVersion(config.error_scenario_path)
        # Save the copy of the error modification that has already ignored data of already deleted error routes
        # fixedErrorModificationFile.tra is the same as the error modification except that it doesn't contain data about deleted routes
    visum1.GenerateModelTransferFileBetweenVersionFiles(
        config.working_scenario_delete_routes_path,
        config.error_scenario_path,
        config.fixed_error_modification_path,
        LayoutFile="",
        NonDefaultOnly=False,
        NonEmptyTablesOnly=True,
        WriteLayoutIntoModelTransferFile=True,
    )

    # Save scenarioErrorFixing.ver (where we add routes back) so taht we can get fixedRouteAddedTransfer.tra by comparing scenarioErrorFixing.ver against scenarioError.ver
    shutil.copy2(
        config.error_scenario_path, config.error_scenario_fixing_routes_path
    ) # error_scenario_path being the error scenario without error routes; error_scenario_fixing_routes_path being the scenario with fixed routes added back

def save_the_routes_deleting_ver(visum, this_project,config):
    """
    Create a transfer file of deleting error routes
    """
    visum.GenerateModelTransferFileBetweenVersionFiles(
        config.working_scenario_path,
        config.working_scenario_delete_routes_path,
        config.route_deleted_transfer_path,
        LayoutFile="",
        NonDefaultOnly=False,
        NonEmptyTablesOnly=True,
        WriteLayoutIntoModelTransferFile=True,
    )
    # Create a new modification in Scenario Management which deletes error routes (i.e. apply routeDeletedTransfer.tra)
    modification1, mod_delete_routes_path, mod_delete_routes_name,mod_delete_routes_id = add_modification( this_project, config, "Erroneous Routes Deleted","Copied from the last working modification and have problematic routes deleted")
    shutil.copy2(
        config.route_deleted_transfer_path, mod_delete_routes_path
    )


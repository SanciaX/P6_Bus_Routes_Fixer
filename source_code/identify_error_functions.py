"""
This module contains functions that help to identify error routes.
"""

import shutil
from visum_sm_functions import add_scenario, add_modification, apply_model_transfer

def read_scenario_management(visum, sm_project, config):
    """Create a new scenario containing the modifications before the error occurs and save the .ver file"""
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

def save_error_routes_n_error_scenario(visum1, visum2, config):
    # Identify and remove erroneous routes which are recognised from the messages file.
    visum2.LoadVersion(config.working_scenario_path) #visum2 links to error route instances
    visum1.LoadVersion(config.working_scenario_path) #visum controls the scenario management project
    routes_dict = {}
    error_route_instances = []
    try:
        with open(config.error_message_path, "r") as fp:
            lines = fp.readlines()
    except FileNotFoundError:
        print("Error: Messages file not found.")
        return routes_dict, error_route_instances

    for line in lines:
        if "Warning Line route" in line or "Error Line route" in line:
            try:
                first_semicolon = line.find(';')
                second_semicolon = line.find(';', first_semicolon + 1)
                route_id = line[first_semicolon + 1:second_semicolon]
                route_no = route_id[:route_id.find(' ')]
                direction = line[second_semicolon + 1:second_semicolon + 2]
                nodes, stops = _get_route_items(route_id,visum2)
                if not route_id in routes_dict:
                    routes_dict[route_id] = {'nodes': nodes, 'stops': stops, 'route id': route_id, 'direction': direction}
                # Save delete_routes.ver and add_routes.ver
                    route_to_delete_instance = visum2.Net.LineRoutes.ItemByKey(route_no, direction, route_id)
                    route_to_remove = visum1.Net.LineRoutes.ItemByKey(route_no, direction, route_id)
                    if route_to_delete_instance:
                        error_route_instances.append(route_to_delete_instance)
                        visum1.Net.RemoveLineRoute(route_to_remove)
            except Exception:
                continue
    visum1.SaveVersion(config.working_scenario_delete_routes_path)

    # Make a copy of the error scenario with error routes deleted
        # Apply the error modification with an anrController to avoid errors that may occur when loading the error modification if the original error modification .tra contains data about error routes that are already deleted
    apply_model_transfer(visum1, config.error_modification)

        # Save the Error Scenario Model with the error routes deleted
    visum1.SaveVersion(config.error_scenario_path)

        # Save the copy of the error modification that has already ignored data of already deleted error routes
    visum1.GenerateModelTransferFileBetweenVersionFiles(
        config.working_scenario_delete_routes_path,
        config.error_scenario_path,
        config.fixed_error_modification_path,
        LayoutFile="",
        NonDefaultOnly=False,
        NonEmptyTablesOnly=True,
        WriteLayoutIntoModelTransferFile=True,
    )

    # Save scenarioError.ver and scenarioErrorFixing.ver for later to build fixedRouteAddedTransfer.tra
    shutil.copy2(
        config.error_scenario_path, config.error_scenario_fixing_routes_path
    ) # error_scenario_path being the error scenario without error routes; error_scenario_fixing_routes_path being the scenario with fixed routes added back
    return routes_dict, error_route_instances

def save_routes_deleting_ver(visum, this_project,config):
    # Create a transfer file of deleting error routes
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


# Internal functions
def _get_route_items(route_id,visum):
    """Retrieves nodes and stops."""
    lineroute = None
    nodes = []
    stops = []
    try:
        for r in visum.Net.LineRoutes.GetAll:
            if r.AttValue("NAME") == route_id:
                lineroute = r
        for item in lineroute.LineRouteItems.GetAll:
            if not item.AttValue("STOPPOINTNO") and item.AttValue("NODENO"):
                stops.append(' ')
                nodes.append(str(int(item.AttValue("NODENO"))))
            elif item.AttValue("STOPPOINTNO") and not item.AttValue("NODENO"):
                stops.append(str(int(item.AttValue("STOPPOINTNO"))))
                nodes.append(' ')
        if lineroute is None:
            print(f"Error retrieving route items for {route_id}")
    except Exception:
        pass

    return nodes, stops

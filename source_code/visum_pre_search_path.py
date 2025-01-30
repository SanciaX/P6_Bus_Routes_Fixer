# source_code/visum_pre_search_path.py
"""
## STEP 1 Load the working scenario to delete erroneous routes and create transfer files (1.deleted and 2.added)
# route_deleted_transfer_file will be used as a new Modification
# route_added_transfer_file_start is where the routes will be fixed and then applied to the problematic
"""

import shutil

def prepare_visum_transferfile(Visum, scenario_management_path, this_project, working_scenario_name, num_of_routes, error_routes, error_dirs,
                        error_directions, working_scenario_delete_routes_name, route_added_transfer_file_start,
                        route_deleted_transfer_file):
    # Load the network before error occurs
    Visum.LoadVersion(working_scenario_name)

    # Delete each route with error and save version
    for route_count in range(num_of_routes):
        error_route_now = error_routes[route_count]
        error_dir = error_dirs[route_count]
        error_direction = error_directions[route_count]
        error_route_name = f"{error_route_now} {error_dir}".strip()
        print(f"Error Route: {error_route_now} {error_dir} ")

        route_to_delete = Visum.Net.LineRoutes.ItemByKey(error_route_now, error_direction, error_route_name)
        if route_to_delete:
            Visum.Net.RemoveLineRoute(route_to_delete)

    Visum.SaveVersion(working_scenario_delete_routes_name)

    # Create a transfer file of adding routes (reverse the deletion action))
    Visum.GenerateModelTransferFileBetweenVersionFiles(
        working_scenario_delete_routes_name,
        working_scenario_name,
        route_added_transfer_file_start,
        LayoutFile="",
        NonDefaultOnly=False,
        NonEmptyTablesOnly=True,
        WriteLayoutIntoModelTransferFile=True,
    )
    # Create a transfer file of adding routes (the deletion action))
    Visum.GenerateModelTransferFileBetweenVersionFiles(
        working_scenario_name,
        working_scenario_delete_routes_name,
        route_deleted_transfer_file,
        LayoutFile="",
        NonDefaultOnly=False,
        NonEmptyTablesOnly=True,
        WriteLayoutIntoModelTransferFile=True,
    )

    # Create a new modification to delete the routes
    new_modification1 = this_project.AddModification()
    new_modification1.SetAttValue("Code", "Erroneous Routes Deleted")
    new_modification1.SetAttValue(
        "Description", "Copied from the last working modification and have problematic routes deleted"
    )
    new_mod_delete_routes = int(new_modification1.AttValue("No"))
    mod_delete_routes_name = new_modification1.AttValue("TraFile")
    str_path = str(scenario_management_path).replace('/', '\\\\')
    mod_delete_routes_file = (
            str_path
            + "\\Modifications\\"+ mod_delete_routes_name
    )
    shutil.copy2(
        route_deleted_transfer_file, mod_delete_routes_file
    )  # copy the transfer file to the path of the scenario management's Modification folder

    return new_mod_delete_routes, mod_delete_routes_name, mod_delete_routes_file
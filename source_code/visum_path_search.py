# source_code/visum_path_search.py

import shutil
import win32com.client
from config.read_json import *
def visum_path_search(c, working_scenario_delete_routes_name, error_modification, error_scenario_network_file_name, node_links, error_route_list, route_added_transfer_file_start, route_added_transfer_file_temp, fix_bus_route_class, route_added_transfer_file_final, modification_check):
    Visum2 = win32com.client.gencache.EnsureDispatch("Visum.Visum.25")
    Visum2.LoadVersion(working_scenario_delete_routes_name)
    Visum2.ApplyModelTransferFile(error_modification)
    Visum2.IO.LoadNet(error_scenario_network_file_name, ReadAdditive=False)

    # Messages in the widget
    all_messages = ""

    # Initialise variables to track state
    n_found = False
    node_start = None
    node_end = None
    search_chains = []  # the list of lists of nodes needing to be added to the route, Note that there may be multiple chains in search_chains

    for i in range(len(node_links)):
        if node_links[i][2] != 1 and not n_found:
            node_start = node_links[i][0]  # Capture the first column value as node_start

            n_found = True  # We found node_start, now we search for node_end
        elif node_links[i][2] == 1 and n_found:
            node_end = node_links[i][0]
            try:
                aNetElementContainer = Visum2.CreateNetElements()
                node1 = Visum2.Net.Nodes.ItemByKey(int(node_start))
                node2 = Visum2.Net.Nodes.ItemByKey(int(node_end))
                aNetElementContainer.Add(node1)
                aNetElementContainer.Add(node2)
                Visum2.Analysis.RouteSearchPrT.Execute(
                    aNetElementContainer, "T", 0, IndexAttribute="SPath"
                )
                NodeChain = Visum2.Analysis.RouteSearchPrT.NodeChainPrT
                chain = [error_route_list[i]]
                for n in range(len(NodeChain)):
                    chain.append(NodeChain[(n+1)].AttValue("NO"))
                if chain != [error_route_list[i]]:  # the first item of search_chains is the route
                    search_chains.append(chain)
                Visum2.Analysis.RouteSearchPrT.Clear()
            except Exception:
                message = f"Warning: Shortest Path is not found between {node_start} and {node_end}."
                all_messages += message + "\n"
            n_found = False

    for each_chain in search_chains: # each chain
        for i in range(1, len(each_chain)):
            each_chain[i] = int(each_chain[i])

    if search_chains:
        all_messages += "Dear Modeller: the following routes have been rerouted through shortest path.\nPlease review the routes and make necessary changes. \n \n"
    for chain in search_chains:
        print(f"Route {chain[0]}: the route between {chain[1]} and {chain[-1]} is found through shortest path search, please review the route in the model.")
        all_messages += f"Route {chain[0]}: the route between {chain[1]} and {chain[-1]} is found through shortest path search, please review the route in the model. \n"
    nodes_delete_list = modification_check.get_nodes_to_delete()
    if search_chains:
        shutil.copy2(
            route_added_transfer_file_start, route_added_transfer_file_temp
        )  # to keep the start file unchanged
        timeprofile = fix_bus_route_class.adjust_routes(error_route_list, error_modification, processed_error_mod_transfer_file,
                      route_added_transfer_file_temp)

        fix_bus_route_class.fix_routes(
            nodes_delete_list, search_chains, route_added_transfer_file_temp
        )
        fix_bus_route_class.fix_profile(route_added_transfer_file_temp, timeprofile)

        shutil.copy2(
            route_added_transfer_file_temp, route_added_transfer_file_final
        )
    Visum3 = win32com.client.gencache.EnsureDispatch("Visum.Visum.25")
    Visum3.LoadVersion(working_scenario_delete_routes_name)
    #Set up anrController to avoid errors that may occur when loading error_modification or route_added_transfer_file_final if .tra contains deleted-route-related item
    anrController = Visum3.IO.CreateAddNetReadController()
    anrController.SetWhatToDo("Line", c.AddNetRead_OverWrite)
    anrController.SetWhatToDo("LineRoute", c.AddNetRead_Ignore)
    anrController.SetWhatToDo("LineRouteItem", c.AddNetRead_Ignore)
    anrController.SetWhatToDo("TimeProfile", c.AddNetRead_Ignore)
    anrController.SetWhatToDo("TimeProfileItem", c.AddNetRead_Ignore)
    anrController.SetWhatToDo("VehJourney", c.AddNetRead_Ignore)
    anrController.SetUseNumericOffset("VehJourney", True)
    anrController.SetWhatToDo("VehJourneyItem", c.AddNetRead_DoNothing)
    anrController.SetWhatToDo("VehJourneySection", c.AddNetRead_Ignore)
    anrController.SetWhatToDo("ChainedUpVehJourneySection", c.AddNetRead_DoNothing)
    anrController.SetWhatToDo("UserAttDef", c.AddNetRead_Ignore)
    anrController.SetWhatToDo("Operator", c.AddNetRead_OverWrite)

    anrController.SetConflictAvoidingForAll(10000, "ORG_")
    Visum3.ApplyModelTransferFile(error_modification, anrController) # CHECK WHAT IF error_modification CONTAINS ROUTE ITEMS RELATED CHANGE THAT MAY LEAD TO AN ERROR
    Visum3.SaveVersion(working_scenario_load_error_mod)
    Visum3.GenerateModelTransferFileBetweenVersionFiles(
        working_scenario_delete_routes_name,
        working_scenario_load_error_mod,
        error_mod_transfer_file,
        LayoutFile="",
        NonDefaultOnly=False,
        NonEmptyTablesOnly=True,
        WriteLayoutIntoModelTransferFile=True,
    )

    Visum3.ApplyModelTransferFile(str(route_added_transfer_file_final), anrController)
    Visum3.SaveVersion(working_scenario_routes_fixed_name)
    Visum3.GenerateModelTransferFileBetweenVersionFiles(
        working_scenario_load_error_mod,
        working_scenario_routes_fixed_name,
        routes_fixed_transfer_file,
        LayoutFile="",
        NonDefaultOnly=False,
        NonEmptyTablesOnly=True,
        WriteLayoutIntoModelTransferFile=True,
    )

    return all_messages, search_chains, nodes_delete_list, error_mod_transfer_file, routes_fixed_transfer_file
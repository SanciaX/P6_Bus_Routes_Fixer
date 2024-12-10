# source_code/visum_path_search.py

import shutil
import win32com.client

def visum_path_search(working_scenario_delete_routes_name, error_modification, network_file_name, node_links, error_route_list, route_added_transfer_file_start, route_transfer_file_temp_name, fix_bus_route_class, route_added_transfer_file_final, modification_check):
    Visum2 = win32com.client.gencache.EnsureDispatch("Visum.Visum.25")
    Visum2.LoadVersion(working_scenario_delete_routes_name)
    Visum2.ApplyModelTransferFile(error_modification)
    Visum2.IO.LoadNet(network_file_name, ReadAdditive=False)

    # Messages in the widget
    all_messages = ""

    # Initialise variables to track state
    n_found = False
    a_n = None
    search_chains = []  # the list of lists of nodes needing to be added to the route

    for i in range(len(node_links)):
        if node_links[i][2] != 1 and not n_found:
            a_n = node_links[i][0]  # Capture the first column value as a_n
            n_found = True  # We found a_n, now we search for a_m

        if node_links[i][2] == 1 and n_found:
            a_m = node_links[i][0]  # Capture the first column value as a_m
            try:
                aNetElementContainer = Visum2.CreateNetElements()
                node1 = Visum2.Net.Nodes.ItemByKey(int(a_n))
                node2 = Visum2.Net.Nodes.ItemByKey(int(a_m))
                aNetElementContainer.Add(node1)
                aNetElementContainer.Add(node2)
                Visum2.Analysis.RouteSearchPrT.Execute(
                    aNetElementContainer, "T", 0, IndexAttribute="SPath"
                )
                NodeChain = Visum2.Analysis.RouteSearchPrT.NodeChainPrT
                chain = [error_route_list[i]]
                for n in range(len(NodeChain)):
                    chain.append(NodeChain[n].AttValue("NO"))
                if chain != [error_route_list[i]]:  # the first item being the route
                    search_chains.append(chain)
                Visum2.Analysis.RouteSearchPrT.Clear()
            except Exception:
                message = f"Warning: Shortest Path is not found between {a_n} and {a_m}."
                all_messages += message + "\n"
            n_found = False

    for sublist in search_chains:
        for i in range(1, len(sublist)):
            sublist[i] = int(sublist[i])

    if search_chains:
        all_messages += "Dear Modeller: the following routes have been rerouted through shortest path. Please review the routes and make necessary changes"
    for chain in search_chains:
        message = f"Route {chain[0]}: please review the route between {chain[1]} and {chain[-1]}"
        print(message)

    nodes_delete_list = modification_check.get_nodes_to_delete()
    if search_chains:
        shutil.copy2(
            route_added_transfer_file_start, route_transfer_file_temp_name
        )  # to keep the start file unchanged
        fix_bus_route_class.fix_routes(
            nodes_delete_list, search_chains, route_transfer_file_temp_name, route_added_transfer_file_final
        )
    Visum3 = win32com.client.gencache.EnsureDispatch("Visum.Visum.25")
    Visum3.LoadVersion(working_scenario_delete_routes_name)
    anrController = Visum3.IO.CreateAddNetReadController()
    anrController.SetWhatToDo("Line", C.AddNetRead_OverWrite)
    anrController.SetWhatToDo("LineRoute", C.AddNetRead_Ignore)
    anrController.SetWhatToDo("LineRouteItem", C.AddNetRead_Ignore)
    anrController.SetWhatToDo("TimeProfile", C.AddNetRead_Ignore)
    anrController.SetWhatToDo("TimeProfileItem", C.AddNetRead_Ignore)
    anrController.SetWhatToDo("VehJourney", C.AddNetRead_Ignore)
    anrController.SetUseNumericOffset("VehJourney", True)
    anrController.SetWhatToDo("VehJourneyItem", C.AddNetRead_DoNothing)
    anrController.SetWhatToDo("VehJourneySection", C.AddNetRead_Ignore)
    anrController.SetWhatToDo("ChainedUpVehJourneySection", C.AddNetRead_DoNothing)
    anrController.SetWhatToDo("UserAttDef", C.AddNetRead_Ignore)
    anrController.SetWhatToDo("Operator", C.AddNetRead_OverWrite)

    anrController.SetConflictAvoidingForAll(10000, "ORG_")
    Visum3.ApplyModelTransferFile(error_modification, anrController)
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

    Visum3.ApplyModelTransferFile(route_added_transfer_file_final, anrController)
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
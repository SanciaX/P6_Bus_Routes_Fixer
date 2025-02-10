# source_code/visum_path_search.py

import shutil
import win32com.client


def visum_path_search(c, working_scenario_delete_routes_name, error_modification, error_scenario_network_file_name, node_links, error_route_list, route_added_transfer_file_start, route_added_transfer_file_temp, fix_bus_route_class, route_added_transfer_file_final, modification_check,network_file_table_of_links,network_file_table_of_turns, check_node_pair_ok_class, processed_error_mod_transfer_file, working_scenario_load_error_mod, error_mod_transfer_file, working_scenario_routes_fixed_name, routes_fixed_transfer_file):

    # Add the route items info. from the erroneous modification to route_added_transfer_file_start and save the node and turn pairs to check between which nodes there should be a shortest path search
    shutil.copy2(
        route_added_transfer_file_start, route_added_transfer_file_temp
    )  # to keep the start file unchanged
    timeprofile, node_pair_list, turn_pair_list = fix_bus_route_class.adjust_routes(error_route_list,
                                                                                    error_modification,
                                                                                    processed_error_mod_transfer_file,
                                                                                    route_added_transfer_file_temp)

    node12_check = []
    for count in node_pair_list:
        node12ok = 999
        check_node1 = count[0]
        check_node2 = count[1]
        check_route1 = count[2]
        check_route2 = count[3]
        with open(network_file_table_of_links, "r") as fp:
            link_lines = fp.readlines()
        for line in link_lines:
            if ";B" in line and line.split(";")[1] == str(check_node1.strip()) and line.split(";")[
                2] == str(check_node2.strip()):  # when there's a link in the current network between two neighbour nodes along a line route and the link is open to bus mode
                if "B," in line or "B;" in line:
                    node12ok = 1 # no link error
        if check_route1 != check_route2:
            node12ok = 2
        if node12ok == 999:
            print(f"Link Error in Route {check_route1} between  {check_node1} and {check_node2}")
        node12_check.append([check_node1, check_node2, node12ok, check_route1])

    turn_pair_ok_list =[]
    for count in turn_pair_list:
        node123ok = 999
        check_node1 = count[0]
        check_node2 = count[1]
        check_node3 = count[2]
        check_route1 = count[3]
        check_route2 =  count[4]
        check_route3 =  count[5]
        with open(network_file_table_of_turns, "r") as fp:
            link_turns = fp.readlines()
            for line in link_turns:
                if line.find(";B") != -1 and line.split(";")[0] == str(check_node1.strip()) and line.split(";")[
                    1] == str(check_node2.strip()) and line.split(";")[
                    2] == str(check_node3.strip()):  # when there's a link in the current network between two neighbour nodes along a line route and the link is open to bus mode
                    if "B," in line or "B;" in line:
                        node123ok = 1 #no turn error
        if check_route1 != check_route3:
            node123ok = 2
        if node123ok == 999:
            print(f"Turn Error in Route {check_route1} between {check_node1} and {check_node3}")
        turn_pair_ok_list.append([check_node1,check_node2, check_node3, check_route1, check_route2, check_route3, node123ok])
    node12_check_additional = []
    for i in range(len(turn_pair_ok_list)):
        if turn_pair_ok_list[i][6] == 999:
            node12_check_additional.append([turn_pair_ok_list[i][0], turn_pair_ok_list[i][1], turn_pair_ok_list[i][3]])
            node12_check_additional.append([turn_pair_ok_list[i][1], turn_pair_ok_list[i][2], turn_pair_ok_list[i][4]])

    for item in range(len(node12_check)):
        for i in range(len(node12_check_additional)):
            if node12_check[item][:2] == node12_check_additional[i][:2] and node12_check[item][3] == node12_check_additional[i][2]:
                node12_check[item][2] = 999

    # Search chains
    Visum2 = win32com.client.gencache.EnsureDispatch("Visum.Visum.25")
    Visum2.LoadVersion(working_scenario_delete_routes_name)
    Visum2.ApplyModelTransferFile(error_modification)
    Visum2.IO.LoadNet(error_scenario_network_file_name, ReadAdditive=False)

    # Messages in the widget
    all_messages = ""

    # Initialise variables to track state
    n_found = False
    node_start = None
    search_chains = []  # the list of lists of nodes needing to be added to the route, Note that there may be multiple chains in search_chains
    mid_nodes_delete = []
    for i in range(len(node12_check)):
        if node12_check[i][2] == 999 and not n_found:
            node_start = node12_check[i][0]  # Capture the first column value as node_start
            n_found = True  # We found node_start, now we search for node_end
            # Starting searching for the shortest path some nodes before the current node, depending on how many nodes there are before the current node
            if i >= 5 and node12_check[i - 5][-1] == node12_check[i][-1]:
                search_start = node12_check[i - 5][0]
                start_index = i - 5
            elif i == 4 and node12_check[i - 4][-1] == node12_check[i][-1]:
                search_start = node12_check[i - 4][0]
                start_index = i - 4
            elif i == 3 and node12_check[i - 3][-1] == node12_check[i][-1]:
                search_start = node12_check[i - 3][0]
                start_index = i - 3
            elif i == 2 and node12_check[i - 2][-1] == node12_check[i][-1]:
                search_start = node12_check[i - 2][0]
                start_index = i - 2
            elif i == 1 and node12_check[i - 1][-1] == node12_check[i][-1]:
                search_start = node12_check[i-1][0]
                start_index = i -1
            else:
                search_start = node12_check[i][0]
                start_index = i
            #offset = max(1, i - 6)
            #search_start = node12_check[offset][0] #the node to start searching for the shortest path
            #start_index = offset # the index of the node to start searching for the shortest path
        elif node12_check[i][2] != 999 and n_found:
            node_end = node12_check[i][0]
            if i <= len(node12_check) - 5 and node12_check[i + 5][-1] == node12_check[i][-1]:
                search_end = node12_check[i + 5][0]
                end_index = i + 5
            elif i == len(node12_check) - 4 and node12_check[i + 4][-1] == node12_check[i][-1]:
                search_end = node12_check[i + 4][0]
                end_index = i + 4
            elif i == len(node12_check) - 3 and node12_check[i + 3][-1] == node12_check[i][-1]:
                search_end = node12_check[i + 3][0]
                end_index = i + 3
            elif i == len(node12_check) - 2 and node12_check[i + 2][-1] == node12_check[i][-1]:
                search_end = node12_check[i + 2][0]
                end_index = i + 2
            elif i == len(node12_check) - 1 and node12_check[i + 1][-1] == node12_check[i][-1]:
                search_end = node12_check[i + 1][0]
                end_index = i + 1
            else:
                search_end = node12_check[i][0]
                end_index = i

            try:
                for i in range(start_index+1, end_index):
                    mid_nodes_delete.append(node12_check[i][0]) # nodes which are along the original routes but need to be deleted as they will be replaced by the node chain(s) searched through shortest path search

                aNetElementContainer = Visum2.CreateNetElements()
                node1 = Visum2.Net.Nodes.ItemByKey(int(search_start))
                node2 = Visum2.Net.Nodes.ItemByKey(int(search_end))
                aNetElementContainer.Add(node1)
                aNetElementContainer.Add(node2)
                Visum2.Analysis.RouteSearchPrT.Execute(
                    aNetElementContainer, "T", 0, IndexAttribute="SPath"
                )
                NodeChain = Visum2.Analysis.RouteSearchPrT.NodeChainPrT
                chain = []
                for n in range(len(NodeChain)):
                    chain.append(NodeChain[(n+1)].AttValue("NO"))
                if chain != []:  # the first item of search_chains is the route
                    search_chains.append([chain,node12_check[i][-1]])
                Visum2.Analysis.RouteSearchPrT.Clear()
            except Exception:
                message = f"Warning: Shortest Path is not found between {node_start} and {node_end}."
                all_messages += message + "\n"
            n_found = False
    if search_chains:
        all_messages += "Dear Modeller: the following routes have been rerouted through shortest path.\nPlease review the routes and make necessary changes. \n \n"
    for chain_route in search_chains:
        print(f"Route {chain_route[1]}: the route between {int(chain_route[0][0])} and {int(chain_route[0][-1])} is found through shortest path search, please review the route in the model.")
        all_messages += f"Route {chain_route[1]}: the route between {int(chain_route[0][0])} and {int(chain_route[0][-1])} is found through shortest path search, please review the route in the model. \n"
    #nodes_delete_list = modification_check.get_nodes_to_delete()
    nodes_delete_list = mid_nodes_delete
    if search_chains:
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
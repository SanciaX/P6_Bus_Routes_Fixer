"""
This file contains functions to fix routes in Visum
"""

def find_error_links(routes_dict, visum1):
    links_on_error_route = []
    nodes = []
    stops = []
    for route_id, route_info in routes_dict.items():
        nodes = route_info.get('nodes', [])
        stops = route_info.get('stops', [])
        nodes_filtered = [node for node in nodes if node != ' ']

        # check links
        links_ok = []
        for i in range(len(nodes_filtered) - 1):
            link_ok = _check_link(visum1, nodes_filtered[i], nodes_filtered[i + 1])
            if not link_ok:
                print(f"Link Error in Route {route_id} between {nodes_filtered[i]} and {nodes_filtered[i + 1]}")
            links_ok.append([nodes_filtered[i], nodes_filtered[i + 1], link_ok])

        # check turns
        turns_ok = []
        for i in range(len(nodes_filtered) - 2):
            turn_ok = _check_turn(visum1, nodes_filtered[i], nodes_filtered[i + 1], nodes_filtered[i + 2])
            if not turn_ok:
                print(f"Turn Error in Route {route_id} from {nodes_filtered[i]} via {nodes_filtered[i + 1]} to {nodes_filtered[i + 2]}")
            turns_ok.append([nodes_filtered[i], nodes_filtered[i + 1], nodes_filtered[i + 2], turn_ok])

            # Update links_ok based on turns_ok
            for t in range(len(turns_ok)):
                if not turns_ok[t][3]:
                    links_ok[t][2] = False
                    links_ok[t + 1][2] = False
        links_on_error_route.append([route_id, links_ok])

    return links_on_error_route, nodes, stops

# Add fixed routes back
def add_routes_back(links_on_error_route, visum3, error_route_instances, nodes, stops, config):
    visum3.LoadVersion(config.error_scenario_fixing_routes_path) # scenarioErrorFixing.ver is the same as scenarioError.ver, but will have fixed routes added back later
    all_messages = ""
    # For each error route
    for i in range(len(links_on_error_route)):
        route, links_ok = links_on_error_route[i]
        route_instance = error_route_instances[i]

        # For each error route, find the start and end node so that the routeitems in between will not be included when adding back new route in the next step
        start_index, end_index, search_start, search_end, all_messages = _find_start_end_nodes(links_ok, nodes, stops, route, all_messages)
        all_messages = _add_one_route_back(start_index, end_index, visum3, route_instance,
                                                                all_messages)
    # Save the transfer file of adding fixed routes back
    visum3.SaveVersion(config.error_scenario_fixing_routes_path)
    visum3.GenerateModelTransferFileBetweenVersionFiles(
        config.error_scenario_path,
        config.error_scenario_fixing_routes_path,
        config.route_fixed_transfer_path,
        LayoutFile="",
        NonDefaultOnly=False,
        NonEmptyTablesOnly=True,
        WriteLayoutIntoModelTransferFile=True,
    )
    return all_messages

# Internal functions
def _check_link(visum1, node1, node2):
    if visum1.Net.Links.LinkExistsByKey(node1, node2):
        for link in visum1.Net.Links.GetAll:
            from_node = str(int(link.AttValue("FROMNODENO")))
            to_node = str(int(link.AttValue("TONODENO")))
            tsysset = link.AttValue("TSYSSET")
            if from_node == node1 and to_node == node2 and "B" in tsysset:
                return True
    return False

def _check_turn(visum1, node1, node2, node3):
    if visum1.Net.Turns.TurnExistsByKey(node1, node2, node3):
        turn = visum1.Net.Turns.ItemByKey(node1, node2, node3)
        if "B" in turn.AttValue("TSYSSET"):
            return True
    return False

def _find_start_end_nodes(links_ok, nodes, stops, route, all_messages):
    n_found = False
    node_before_errors = None
    node_after_errors = None
    for i in range(len(links_ok)):
        if not links_ok[i][2] and not n_found: # links_ok[i][2] of an error link is False
            n_found = True
            node_before_errors = links_ok[i][0]
            break
    for i in range(len(links_ok) - 1, -1, -1):
        if not links_ok[i][2]:
            node_after_errors = links_ok[i + 1][0]
            break
    if not node_before_errors and not node_after_errors:
        node_before_errors = links_ok[0][1]
        node_after_errors = links_ok[1][1]
    if node_before_errors and not node_after_errors:
        node_after_errors = links_ok[-1][1]
    node_before_errors_idx = nodes.index(node_before_errors)
    node_after_errors_idx = nodes.index(node_after_errors)
    search_start = nodes[0]
    search_end = nodes[-1]
    for i in range(node_before_errors_idx - 1, -1, -1):
        if stops[i] != ' ':  # if the route_item is a stop
            search_start = nodes[
                (i + 1)]  # search start from the node after the last stop which is before link/turn error(s)
            break
    for i in range(node_after_errors_idx + 1, len(nodes)):
        if stops[i] != ' ':  # if the route_item is a stop:
            search_end = nodes[
                (i - 1)]  # search ends at the node before the next stop which is after link/turn error(s)
            break
    start_index = nodes.index(search_start)
    end_index = nodes.index(search_end)
    message = f"check the route between {search_start} and {search_end} for Route {route}."
    all_messages += message + "\n"
    return start_index, end_index, search_start, search_end, all_messages

            
def _add_one_route_back(start_index, end_index, visum3, route_instance, all_messages):
    try:
        name = route_instance.AttValue("NAME")
        line = visum3.Net.Lines.ItemByKey(name.split(' ')[0])
        direction = visum3.Net.Directions.GetAll[0]
        for dirTo in visum3.Net.Directions.GetAll:
            if dirTo.AttValue("CODE") == route_instance.AttValue("DIRECTIONCODE"):
                direction = dirTo
        paraR1 = visum3.IO.CreateNetReadRouteSearchTSys()  # create the parameter object
        paraR1.SetAttValue("HowToHandleIncompleteRoute", 2)  # search the shortest path if line route has gaps
        paraR1.SetAttValue("ShortestPathCriterion", 3)  # 3:Link length; 0 Direct distance ; 1 Link travel time of current transport system; 2 Link type travel time of current transport system
        paraR1.SetAttValue("IncludeBlockedLinks", False)  # don't route over closed links
        paraR1.SetAttValue("IncludeBlockedTurns", False)  # don't route over closed turns
        paraR1.SetAttValue("MaxDeviationFactor", 1000)  # maximum deviation factor of shortest path search from direct distance
        paraR1.SetAttValue("WhatToDoIfShortestPathNotFound", 0)  # 0 Do not read ; 2 Insert link if necessary ; 1 Open link or turn for transport system

        route_items= visum3.CreateNetElements()
        items = route_instance.LineRouteItems.GetAll[:(start_index+1)] + route_instance.LineRouteItems.GetAll[end_index:]
        for item in items:
            stoppoint = item.AttValue("STOPPOINTNO")
            node = item.AttValue("NODENO")
            if stoppoint:
                stop = visum3.Net.StopPoints.ItemByKey(stoppoint)
                route_items.Add(stop)
            else:
                node = visum3.Net.Nodes.ItemByKey(node)
                route_items.Add(node)
        visum3.Net.AddLineRoute(name, line, direction, route_items, paraR1)
        ##### NEED TO ADD TIME PROFILE

    except Exception:
        message = f"Not be able to generate a fixed route."
        all_messages += message + "\n"
    return all_messages


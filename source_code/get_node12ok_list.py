# source_code/get_node12ok_list.py

def get_node12ok_list(error_route_mojibake, routenodes, errornodelist, errornodestoplist, modificationchecklist,  route_added_transfer_file_start, network_file_name, network_file_table_of_links, network_file_table_of_turns, error_modification, error_nodes_check, error_nodes_type_check, check_node_pair_ok_class):
    route_node_class = routenodes(route_added_transfer_file_start)  # read from route_added_transfer_file_start
    error_node_list_class = errornodelist()
    error_node_stop_list_class = errornodestoplist()
    route_node_class.read_route_file(
        error_node_list_class, error_node_stop_list_class
    )  # get the list of nodes and the nested list of nodes and stops
    error_node_stop_list = error_node_stop_list_class.get_node_stop_list  # error_node_stop_list is a nested list
    num_of_node_stop = error_node_stop_list_class.get_nodes_stop_count()
    error_route_list_long = error_node_stop_list_class.get_route()
    error_routes_nodes_list = error_node_list_class.check_node1()
    num_of_nodes = error_node_list_class.error_num_nodes()
    print(f"Number of nodes along the route(s): {num_of_nodes}")
    
    error_route_list = error_node_list_class.error_route_id()
    error_node_pairs_list = [
    [error_routes_nodes_list[i], error_routes_nodes_list[i + 1], error_route_list[i], error_route_list[i + 1]]
    for i in range(len(error_routes_nodes_list) - 1)
    ]
    # Filter repetitive node pairs
    filtered_node_pairs_list = []
    seen_pairs = set()
    for row in error_node_pairs_list:
        pair = (row[0], row[1])
        if pair not in seen_pairs:
            filtered_node_pairs_list.append(row)
            seen_pairs.add(pair)
    error_node_pairs_list = filtered_node_pairs_list

    error_node_turns_list =  [
    [error_routes_nodes_list[i], error_routes_nodes_list[i + 1], error_routes_nodes_list[i + 1], error_route_list[i], error_route_list[i+1], error_route_list[i + 2]]
    for i in range(len(error_routes_nodes_list) - 2)
    ] #  :params: [node1, node2, node3, route of node1, route of node2, route of node3]  only when route1,2,3 are the same, we check the turn
    # Filter repetitive turns
    filtered_node_turns_list = []
    seen_turns = set()
    for row in error_node_turns_list:
        turn = (row[0], row[1], row[2])
        if turn not in seen_turns:
            filtered_node_turns_list.append(row)
            seen_turns.add(turn)
    error_node_turns_list = filtered_node_turns_list
    
    start_marker_link = "$LINK:NO"
    end_marker_link = "$LINKPOLY"
    with open(network_file_name, "r") as fp: # network_file_name: network of the scenario with error(s)
        lines = fp.readlines()
    in_between = False
    result_lines = []
    for line in lines:
        if start_marker_link in line:
            in_between = True  # Start keeping lines
        if in_between:
            result_lines.append(line) # result_lines contains the table of links in the error network
        if end_marker_link in line:
            in_between = False  # Stop keeping lines
    with open(network_file_table_of_links, "w") as output:
        output.writelines(result_lines)

    start_marker_turn = "$TURN:"
    end_marker_turn = "* Table: Main turns"
    with open(network_file_name, "r") as fp:  # network_file_name: network of the scenario with error(s)
        lines = fp.readlines()
    in_between = False
    result_lines = []
    for line in lines:
        if start_marker_turn in line:
            in_between = True  # Start keeping lines
        if in_between:
            result_lines.append(line)  # result_lines contains the table of links in the error network
        if end_marker_turn in line:
            in_between = False  # Stop keeping lines
    with open(network_file_table_of_turns, "w") as output:
        output.writelines(result_lines)

    #counting_node = 0
    node_links = []
    # The pairs of nodes recognized through "for count in range(num_of_nodes-1)" iteration are all successive nodes along the original route
    for count in range(len(error_node_pairs_list)): # -1 because number of node pairs = number of nodes - 1
        check_node1 = [row[0] for row in error_node_pairs_list][count]
        check_node2 = [row[1] for row in error_node_pairs_list][count]
        check_route_this_node =[row[2] for row in error_node_pairs_list][count]
        check_route_of_next_node = [row[3] for row in error_node_pairs_list][count]
        node12ok = check_node_pair_ok_class.check_nodes_errorlink(
            count,
            check_node1,
            check_node2,
            check_route_this_node,
            check_route_of_next_node,
            error_nodes_check,
            error_nodes_type_check,
            error_route_mojibake
        )
        node_links.append([check_node1, check_node2, node12ok])

    node_turns = []
    # The pairs of nodes recognized through "for count in range(num_of_nodes-1)" iteration are all successive nodes along the original route
    for count in range(len(error_node_turns_list)):  # -1 because number of node pairs = number of nodes - 1
        check_node1 = [row[0] for row in error_node_turns_list][count]
        check_node2 = [row[1] for row in error_node_turns_list][count]
        check_node3 = [row[2] for row in error_node_turns_list][count]
        check_route_node1 = [row[3] for row in error_node_turns_list][count]
        check_route_node3 = [row[5] for row in error_node_turns_list][count]
        node123ok = check_node_pair_ok_class.get_nodes_errorturn(
            count,
            check_node1,
            check_node2,
            check_node3,
            check_route_node1,
            check_route_node3,
            error_nodes_check,
            error_nodes_type_check,
            error_route_mojibake
        )
        node_turns.append([check_node1, check_node2, check_node3, node123ok])


    # Problematic nodes read from the modification file (.tra)
    modification_check = modificationchecklist()
    modification_check.set_links_to_check(error_modification, error_routes_nodes_list)
    node_links_replace = modification_check.get_links_to_check()
    node_links_replace = [[str(x), str(y), z] for x, y, z in node_links_replace]

    # Update node_links with replacements
    for replace in node_links_replace:
        for link in node_links:
            if replace[0] == link[0] and replace[1] == link[1]:
                link[2] = replace[2]

    return modification_check, node_links, error_node_stop_list, num_of_node_stop, error_route_list_long, error_routes_nodes_list, error_route_list, num_of_nodes
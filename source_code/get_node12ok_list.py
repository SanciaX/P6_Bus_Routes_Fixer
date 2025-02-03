# source_code/get_node12ok_list.py

def get_node12ok_list(error_route_mojibake, routenodes, errornodelist, errornodestoplist, modificationchecklist,  route_added_transfer_file_start, error_scenario_network_file_name, network_file_table_of_links, network_file_table_of_turns, error_modification, error_nodes_check, error_nodes_type_check, check_node_pair_ok_class):
    route_node_class = routenodes(route_added_transfer_file_start, error_modification)  # read from route_added_transfer_file_start
    #route_node_deleted_class = routenodes(route_added_transfer_file_start, error_modification) # the nodes list from the erroneous modification's Table: Line route items (Element deleted)
    #route_node_added_class = routenodes(route_added_transfer_file_start, error_modification) # the nodes list from the erroneous modification's Table: Line route items (Element inserted)
    error_node_list_class = errornodelist()
    error_node_stop_list_class = errornodestoplist()
    route_node_class.read_route_file(
        error_node_list_class, error_node_stop_list_class
    )  # get the list of nodes and the nested list of nodes and stops
    #route_node_added_class.read_route_file(
    #    error_node_list_class, error_node_stop_list_class
    #)
    route_node_class.delete_route_items_from_mod(error_node_list_class, error_node_stop_list_class)
    route_node_class.add_route_items_from_mod(error_node_list_class, error_node_stop_list_class)

    error_node_stop_list = error_node_stop_list_class.get_node_stop_list  # error_node_stop_list is a nested list
    num_of_node_stop = error_node_stop_list_class.get_nodes_stop_count()
    error_route_list_long = error_node_stop_list_class.get_route()
    nodes_list = error_node_list_class.check_node1()
    num_of_nodes = error_node_list_class.error_num_nodes()
    routes_list = error_node_list_class.error_route_id()
    error_node_route_list = [[nodes_list[i], routes_list[i]] for i in range(len(nodes_list))]

    delete_nodes_index = []
    delete_nodes_routes = []
    insert_nodes_index = []
    insert_nodes_routes = []
    nodes_index = []
    nodes_routes = []
    for i in range(len(nodes_list)):
       if 'delete' in routes_list[i]:
           delete_nodes_index.append(i)
           delete_nodes_routes.append([nodes_list[i],[routes_list[i]]])
       elif 'insert' in routes_list[i]:
           insert_nodes_index.append(i)
           insert_nodes_routes.append([nodes_list[i], [routes_list[i]]])
       else:
           nodes_index.append(i)
           nodes_routes.append([nodes_list[i], [routes_list[i]]])
    delete = [False] * len(nodes_index)
    for n in range(len(nodes_index)):
        for m in range(len(delete_nodes_index)):
            if nodes_routes[n][0] == delete_nodes_routes[m][0] and nodes_routes[n][1][0] in delete_nodes_routes[m][1][0]:
                delete[n] = True
    filtered_nodes_routes = [node for node, to_keep in zip(nodes_routes, delete) if not to_keep]
    for row in filtered_nodes_routes:
        row[1] = row[1][0]

    with open(error_modification, "r") as fp:
        lines = fp.readlines()
        start_table_index = False
        node_route_stop_nextn_nexts_to_insert_list = []
        for line in lines:
            if '* Table: Line route items (Element inserted)' in line:
                start_table_index = True
            elif '* Table' in line and start_table_index:
                break
            if start_table_index:
                if "B;" in line:
                    node_route_stop_nextn_nexts_to_insert_list.append([line.split(";")[3], line.split(";")[1], line.split(";")[4],line.split(";")[6],line.split(";")[7]])

    updated_nodes_routes = []
    insert_next = False
    start_insert = False

    for n in range(len(filtered_nodes_routes) - 1):
        updated_nodes_routes.append(filtered_nodes_routes[n])
        for m in range(len(node_route_stop_nextn_nexts_to_insert_list) - 1):
            # when finding the first row to start inserting
            if filtered_nodes_routes[n][0] == node_route_stop_nextn_nexts_to_insert_list[0][0] and \
                    filtered_nodes_routes[n][1] == node_route_stop_nextn_nexts_to_insert_list[0][
                1] and not start_insert and not insert_next:
                start_insert = True
                if (node_route_stop_nextn_nexts_to_insert_list[0][-2] ==
                    node_route_stop_nextn_nexts_to_insert_list[0 + 1][0] and
                    node_route_stop_nextn_nexts_to_insert_list[0][-2] != '') or (
                        node_route_stop_nextn_nexts_to_insert_list[0][-1] ==
                        node_route_stop_nextn_nexts_to_insert_list[0 + 1][2] and
                        node_route_stop_nextn_nexts_to_insert_list[0][-1] != ''):
                    insert_next = True
                    node_route_stop_nextn_nexts_to_insert_list = node_route_stop_nextn_nexts_to_insert_list[1:]
                else:
                    insert_next = False
                    node_route_stop_nextn_nexts_to_insert_list = node_route_stop_nextn_nexts_to_insert_list[1:]
            elif filtered_nodes_routes[n][0] != node_route_stop_nextn_nexts_to_insert_list[0][0] and \
                    filtered_nodes_routes[n][1] == node_route_stop_nextn_nexts_to_insert_list[0][1] and start_insert:
                if insert_next:
                    updated_nodes_routes.append(
                        [node_route_stop_nextn_nexts_to_insert_list[0][0],
                         node_route_stop_nextn_nexts_to_insert_list[0][1]])
                    if (node_route_stop_nextn_nexts_to_insert_list[0][-2] ==
                        node_route_stop_nextn_nexts_to_insert_list[0 + 1][0] and
                        node_route_stop_nextn_nexts_to_insert_list[0][-2] != '') or (
                            node_route_stop_nextn_nexts_to_insert_list[0][-1] ==
                            node_route_stop_nextn_nexts_to_insert_list[0 + 1][2] and
                            node_route_stop_nextn_nexts_to_insert_list[0][-1] != ''):
                        insert_next = True
                        node_route_stop_nextn_nexts_to_insert_list = node_route_stop_nextn_nexts_to_insert_list[1:]
                    else:
                        insert_next = False
                        start_insert = False

                        node_route_stop_nextn_nexts_to_insert_list = node_route_stop_nextn_nexts_to_insert_list[1:]
                        break
            if len(node_route_stop_nextn_nexts_to_insert_list)==1:
                updated_nodes_routes.append(
                    [node_route_stop_nextn_nexts_to_insert_list[0][3],
                     node_route_stop_nextn_nexts_to_insert_list[0][1]])

    updated_nodes_routes = [row for row in updated_nodes_routes if row[0] != '']

    node_pairs_list = [[updated_nodes_routes[i][0], updated_nodes_routes[i + 1][0], updated_nodes_routes[i][1], updated_nodes_routes[i + 1][1]] for i in range(len(updated_nodes_routes) - 1)]
    print(f"Number of nodes along the route(s) (after deleting and adding route items in the erroneous modification if there are any): {len(updated_nodes_routes)}")

    # Filter repetitive node pairs
    filtered_node_pairs_list = []
    seen_pairs = set()
    for row in node_pairs_list:
        pair = (row[0], row[1])
        if pair not in seen_pairs:
            filtered_node_pairs_list.append(row)
            seen_pairs.add(pair)
    node_pairs_list = filtered_node_pairs_list

    node_turns_list = [[updated_nodes_routes[i][0], updated_nodes_routes[i + 1][0], updated_nodes_routes[i + 2][0], updated_nodes_routes[i][1], updated_nodes_routes[i + 1][1], updated_nodes_routes[i + 2][1]] for i in range(len(updated_nodes_routes) - 2)]

    # Filter repetitive turns
    filtered_node_turns_list = []
    seen_turns = set()
    for row in node_turns_list:
        turn = (row[0], row[1], row[2])
        if turn not in seen_turns:
            filtered_node_turns_list.append(row)
            seen_turns.add(turn)
    node_turns_list = filtered_node_turns_list

############################################################
##### DO NOT DELETE BELOW CODES!!!!!
    # Below is needed to save turn tables and link tables of the erroneous network!!!
    start_marker_link = "$LINK:NO"
    end_marker_link = "$LINKPOLY"
    with open(error_scenario_network_file_name, "r") as fp: # error_scenario_network_file_name: network of the scenario with error(s)
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
    with open(error_scenario_network_file_name, "r") as fp:  # error_scenario_network_file_name: network of the scenario with error(s)
        lines = fp.readlines()
    in_between = False
    result_lines = []
    for line in lines:
        if start_marker_turn in line:
            in_between = True  # Start keeping lines
        if end_marker_turn in line:
            in_between = False  # Stop keeping lines
        if in_between:
            result_lines.append(line)  # result_lines contains the table of links in the error network

    with open(network_file_table_of_turns, "w") as output:
        output.writelines(result_lines)
    ############################################################

    #counting_node = 0
    node_links = []
    # The pairs of nodes recognized through "for count in range(num_of_nodes-1)" iteration are all successive nodes along the original route
    for count in range(len(node_pairs_list)): # -1 because number of node pairs = number of nodes - 1
        check_node1 = [row[0] for row in node_pairs_list][count]
        check_node2 = [row[1] for row in node_pairs_list][count]
        check_route_this_node =[row[2] for row in node_pairs_list][count]
        check_route_of_next_node = [row[3] for row in node_pairs_list][count]
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
        node_links.append([check_node1, check_node2, node12ok]) #For which node12ok value notes which error type, see 'check_node12_ok.py

    node_turns = []
    # The pairs of nodes recognized through "for count in range(num_of_nodes-1)" iteration are all successive nodes along the original route
    for count in range(len(node_turns_list)):
        check_node1 = [row[0] for row in node_turns_list][count]
        check_node2 = [row[1] for row in node_turns_list][count]
        check_node3 = [row[2] for row in node_turns_list][count]
        check_route_node1 = [row[3] for row in node_turns_list][count]
        check_route_node3 = [row[5] for row in node_turns_list][count]
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

    for turn in node_turns:
        if turn[-1] != 1:
            node1, node2, node3 = [turn[0], turn[1], turn[2]]
            #print('Turn error: ', node1, node2)
            #print('Turn error: ', node2, node3)
            for i in range(len(node_links)):
                if node_links[i][0] == node1 and node_links[i][1] == node2:
                    node_links[i][2] = 999
                if node_links[i][0] == node2 and node_links[i][1] == node3:
                    node_links[i][2] = 999

    # Problematic nodes read from the modification file (.tra)
    modification_check = modificationchecklist()
    modification_check.set_links_to_check(error_modification, nodes_list)
    node_links_replace = modification_check.get_links_to_check() # [node1, node2, error_type_code]
    node_links_replace = [[str(x), str(y), z] for x, y, z in node_links_replace]

    # Update node_links with replacements, especially when node_links shows no problem while there are potential errors found in the modification file
    for replace in node_links_replace:
        for link in node_links:
            if replace[0] == link[0] and replace[1] == link[1]:
                link[2] = replace[2]

    return modification_check, node_links, error_node_stop_list, num_of_node_stop, error_route_list_long, nodes_list, routes_list, num_of_nodes
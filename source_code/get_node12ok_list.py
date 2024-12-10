# source_code/get_node12ok_list.py

def get_node12ok_list(routenodes, errornodelist, errornodestoplist, modificationchecklist,  route_added_transfer_file_start, network_file_name, network_file_name_short, error_modification, error_nodes_check, error_nodes_type_check, node12ok_class):
    route_node_class = routenodes(route_added_transfer_file_start)  # read from route_added_transfer_file_start
    error_node_list_class = errornodelist()
    error_node_stop_list_class = errornodestoplist()
    route_node_class.read_route_file(
        error_node_list_class, error_node_stop_list_class
    )  # get the list of nodes and the nested list of nodes and stops
    error_node_stop_list = error_node_stop_list_class.get_node_stop_list  # error_node_stop_list is a nested list
    num_of_node_stop = error_node_stop_list_class.get_nodes_stop_count()
    error_route_list_long = error_node_stop_list_class.get_route()
    error_node_list1 = error_node_list_class.check_node1()
    error_route_list = error_node_list_class.error_route_id()

    num_of_nodes = error_node_list_class.error_num_nodes()
    print(f"Number of nodes along the route(s): {num_of_nodes}")

    start_marker = "$LINK:NO"
    end_marker = "$LINKPOLY"
    with open(network_file_name, "r") as fp:
        lines = fp.readlines()
    in_between = False
    result_lines = []
    for line in lines:
        if start_marker in line:
            in_between = True  # Start keeping lines
        if in_between:
            result_lines.append(line)
        if end_marker in line:
            in_between = False  # Stop keeping lines
    with open(network_file_name_short, "w") as output:
        output.writelines(result_lines)

    #counting_node = 0
    node_links = []

    # The pairs of nodes recognized through "for count in range(num_of_nodes-1)" iteration are all successive nodes along the original route
    for count in range(num_of_nodes - 1):
        check_node1 = error_node_list1[count]
        check_node2 = error_node_list1[count + 1]
        check_route_this_node = error_route_list[count]
        check_route_of_next_node = error_route_list[count + 1]
        node12ok = node12ok_class.get_error_nodes2(
            count,
            check_node1,
            check_node2,
            check_route_this_node,
            check_route_of_next_node,
            error_nodes_check,
            error_nodes_type_check,
        )  # return 999 or 1 or the missing node that can be solved by Birendra's method
        node_links.append([check_node1, check_node2, node12ok])

    # Problematic nodes read from the modification file (.tra)
    modification_check = modificationchecklist()
    modification_check.set_links_to_check(error_modification, error_node_list1)
    node_links_replace = modification_check.get_links_to_check()
    node_links_replace = [[str(x), str(y), z] for x, y, z in node_links_replace]

    # Update node_links with replacements
    for replace in node_links_replace:
        for link in node_links:
            if replace[0] == link[0] and replace[1] == link[1]:
                link[2] = replace[2]

    return modification_check, node_links, error_node_stop_list, num_of_node_stop, error_route_list_long, error_node_list1, error_route_list, num_of_nodes
from source_code.node_checklist import NodeCheckList
from source_code.error_reading import ErrorNodes, ModificationCheckList
from source_code.route_nodes import RouteNodes
from source_code.error_node_stop_route_lists import ErrorNodeStopList, ErrorNodeList, ErrorRouteList
from source_code.check_node12_ok import CheckNodePairOk
from source_code.fix_bus_route import FixBusRoute

def identify_errors(error_message_file, network_file_table_of_links, network_file_table_of_turns):
    error_nodes_class = ErrorNodes(error_message_file)  # read error message
    node_check_list_class = NodeCheckList()
    error_route_list_class = ErrorRouteList()  # the list of error routes
    error_route_mojibake = error_nodes_class.get_route_mojibake()
    ## Read error file and process routes
    error_nodes_class.read_error_file(error_route_list_class, node_check_list_class)
            # 1. whenever there's a new (node1, node2, error_type), append it node1, node2 and error_type lists
            # 2. when there's a line of Error/Warning Line route message, error_route_list_class.get_error_route(counter1, bus_route_number, bus_route_dir, direction)
            # 3. as such, UNLESS THERE ARE ERROR 'mojibake', the len of list of check_node1 or check_node2 equals to the number of error node pairs
            # 4. the len of error_route equals to the number of error routes, except for error 'mojibake'
            # return route_num, e.g. [['1', 0, 0 ...]
    error_routes = error_route_list_class.error_route()
    error_route_names = error_route_list_class.error_route_name()
    error_dirs = error_route_list_class.error_dir()
    error_directions = error_route_list_class.error_direction()
    error_nodes_checklist = node_check_list_class.check_node1()  # list of all the nodes to check
    #  return self.node1 -> self.node1[counter] = node1 -> error_node_list_class.get_error_nodes(counter1, node_num, current_route)
    error_nodes_checklist2 = node_check_list_class.check_node2()
    error_node_type_checklist = node_check_list_class.get_error_type()  # list of
    error_nodes_check = [
        (error_nodes_checklist[i], error_nodes_checklist2[i]) for i in range(len(error_nodes_checklist))
    ]
    error_nodes_type_check = [
        (error_nodes_checklist[i], error_nodes_checklist2[i], error_node_type_checklist[i])
        for i in range(len(error_nodes_checklist))
    ]
    print(f"Nodes to check and error types: {error_nodes_type_check}")

    check_node_pair_ok_class = CheckNodePairOk(network_file_table_of_links, network_file_table_of_turns)
    fix_bus_route_class = FixBusRoute()

    num_of_routes = error_route_list_class.error_route_count()
    error_route = error_routes[1]
    print(f"Number of Routes: {num_of_routes}")

    return error_route_mojibake, error_dirs, error_directions, error_nodes_check, error_route_names, error_route, error_nodes_class, node_check_list_class, error_route_list_class, check_node_pair_ok_class, fix_bus_route_class, num_of_routes, error_routes, error_nodes_type_check
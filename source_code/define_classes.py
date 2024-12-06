from source_code.node_checklist import NodeCheckList
from source_code.error_reading import ErrorNodes, ModificationCheckList
from source_code.route_nodes import RouteNodes
from source_code.error_node_stop_route_lists import ErrorNodeStopList, ErrorNodeList, ErrorRouteList
from source_code.check_node12_ok import CheckNode12ok
from source_code.fix_bus_route import FixBusRoute

def initialize_classes(error_message_file, network_file_name_short):
    error_node_class = ErrorNodes(error_message_file)  # read error message
    node_check_list_class = NodeCheckList()
    error_route_list_class = ErrorRouteList()  # the list of error routes

    # Read error file and process routes
    error_node_class.read_error_file(error_route_list_class, node_check_list_class)  # get error route: call error_route_list_class.get_error_route method, in which calls errorRouteList_Class.get_error_route(counter1,busRouteNumber,busRouteDir,direction)
    error_route_list = error_route_list_class.error_route()  # Return route_num
    error_dir_list = error_route_list_class.error_dir()
    error_direction_list = error_route_list_class.error_direction()
    error_nodes_checklist = node_check_list_class.get_check_node1()  # list of all the nodes to check
    error_nodes_checklist2 = node_check_list_class.get_check_node2()
    error_node_type_checklist = node_check_list_class.get_error_type()  # list of
    error_nodes_check = [
        (error_nodes_checklist[i], error_nodes_checklist2[i]) for i in range(len(error_nodes_checklist))
    ]
    error_nodes_type_check = [
        (error_nodes_checklist[i], error_nodes_checklist2[i], error_node_type_checklist[i])
        for i in range(len(error_nodes_checklist))
    ]
    print(f"Nodes to check and error types: {error_nodes_type_check}")

    node12ok_class = CheckNode12ok(network_file_name_short)
    fix_bus_route_class = FixBusRoute()

    num_of_routes = error_route_list_class.error_route_count()
    error_route = error_route_list[1]
    print(f"Number of Routes: {num_of_routes}")

    return error_dir_list, error_direction_list, error_nodes_check, error_route, error_node_class, node_check_list_class, error_route_list_class, node12ok_class, fix_bus_route_class, num_of_routes, error_route_list, error_nodes_type_check
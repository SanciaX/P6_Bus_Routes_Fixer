"""Read the transfer file that adds fixed routes back"""

class RouteNodes:
    def __init__(self, route_added_transfer_file_start,error_modification):
        self.route_added_transfer_file_start = route_added_transfer_file_start
        self.error_modification = error_modification
        self.word3 = "$+LINEROUTEITEM"  # Start
        self.word4 = "$+TIMEPROFILE"  # End
        self.routeNumber = 0

    def read_route_file(self, error_node_list_class, node_stop_list_class):
        with open(self.route_added_transfer_file_start, "r") as fp:
            # route_added_transfer_file_start is defined in the beginning of the main script
            lines = fp.readlines()
            start_line_index = False
            current_route = "0 "
            last_route = "0 "
            for line in lines:
                if self.word4 in line:
                    break
                if start_line_index:
                    if "B;" in line:
                        node_stop = line.split(";")[3:5]
                        node_stop_list_class.get_node_stop( node_stop, current_route)
                        node_num = line.split(";")[3]
                        current_route = line.split(";")[1]
                        if node_num.isdigit() and current_route == last_route:
                            error_node_list_class.get_error_nodes(node_num, current_route)
                        last_route = current_route
                if self.word3 in line:
                    start_line_index = True

    def read_route_file_from_mod(self, error_node_list_class, node_stop_list_class):
        with open(self.error_modification, "r") as fp:
            lines = fp.readlines()
            start_table_index = False
            current_route = "0 "
            last_route = "0 "
            for line in lines:
                if '* Table: Line route items (Element inserted)' in line:
                    start_table_index = True
                if self.word4 in line and start_table_index:
                    break
                if start_table_index:
                    if "B;" in line:
                        node_stop = line.split(";")[3:5]
                        node_stop_list_class.get_node_stop(node_stop, current_route)
                        node_num = line.split(";")[3]
                        current_route = line.split(";")[1] + ' recognized from the errorneous modification'
                        if node_num.isdigit() and current_route == last_route:
                            error_node_list_class.get_error_nodes(node_num, current_route)
                        last_route = current_route


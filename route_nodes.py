"""Read the transfer file that adds fixed routes back"""

class RouteNodes:
    def __init__(self, route_added_transfer_file_start):
        self.route_added_transfer_file_start = route_added_transfer_file_start
        self.word3 = "$+LINEROUTEITEM"  # Start
        self.word4 = "$+TIMEPROFILE"  # End
        self.routeNumber = 0

    def read_route_file(self, error_node_list_class, node_stop_list_class):
        with open(self.route_added_transfer_file_start, "r") as fp:
            # routeAddedTransferFileStart is defined in the beginning of the main script
            lines = fp.readlines()
            start_line_index = False
            counter1 = -1
            counter2 = -1
            current_route = "0 "
            last_route = "0 "

            for line in lines:
                if self.word4 in line:
                    break
                if start_line_index:
                    if "B;" in line:
                        node_stop = line.split(";")[3:5]
                        counter2 += 1
                        node_stop_list_class.get_node_stop(counter2, node_stop, current_route)
                        node_num = line.split(";")[3]
                        current_route = line.split(";")[1]
                        if node_num.isdigit() and current_route == last_route:
                            counter1 += 1
                            error_node_list_class.get_error_nodes(counter1, node_num, current_route)
                        last_route = current_route
                if self.word3 in line:
                    start_line_index = True
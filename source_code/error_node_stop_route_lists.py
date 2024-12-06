"""
Read the list of Nodes and Stops along the problematic route(s)
in case stops may be needed in future version
"""
class ErrorNodeStopList:
    def __init__(self):
        self.get_node_stop_list = [[0, 0] for _ in range(10000)]
        self.route_name2 = [0] * 10000
        self.counter = 0

    def get_node_stop(self, counter, node_stop, this_route):
        self.get_node_stop_list[counter] = node_stop
        self.route_name2[counter] = this_route
        self.counter = counter

    def get_nodes_stop_count(self):
        return self.counter

    def get_from_stop(self):
        return self.get_node_stop_list[0][1]

    def get_to_stop(self):
        return self.get_node_stop_list[self.counter][1]

    def get_route(self):
        return self.route_name2

"""Read the list of nodes along the problematic route(s)"""
class ErrorNodeList:
    def __init__(self):
        self.node1 = [0] * 10000
        self.node2 = [0] * 10000
        self.routeName = [0] * 10000
        self.counter = 0
        self.currentRoute = ["0 "] * 10000

    def get_error_nodes(self, counter, node1, current_route):
        self.node1[counter] = node1
        self.counter = counter
        self.currentRoute[counter] = current_route

    def check_node1(self):
        return self.node1

    def error_num_nodes(self):
        return self.counter  # num_of_nodes

    def error_route_id(self):
        return self.currentRoute


""" the list of error routes"""
class ErrorRouteList:
    def __init__(self):
        self.route_num = [0] * 100
        self.route_dir = [0] * 100
        self.route_direction = [0] * 100
        self.route_name_check = 0
        self.counting1 = 0
        self.counting2 = 0

    def get_error_route(self, counter_route, route_num, route_dir, route_direction):
        if counter_route == 0:
            self.counting1 = 0
            self.route_num[self.counting1] = route_num
            self.route_dir[self.counting1] = route_dir
            self.route_direction[self.counting1] = route_direction
            self.route_name_check = route_num + route_direction

        if self.route_name_check != route_num + route_direction:
            self.counting1 += 1
            self.route_num[self.counting1] = route_num
            self.route_dir[self.counting1] = route_dir
            self.route_direction[self.counting1] = route_direction
            self.route_name_check = route_num + route_direction

    def error_route(self):
        return self.route_num

    def error_dir(self):
        return self.route_dir

    def error_direction(self):
        return self.route_direction

    #def error_line_direction(self):
        #return self.lineDirection

    def error_route_count(self):
        self.counting2 = self.counting1 + 1
        return self.counting2

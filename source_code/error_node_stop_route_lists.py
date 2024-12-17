"""
Read the list of Nodes and Stops along the problematic route(s)
in case stops may be needed in future version
"""
class ErrorNodeStopList:
    def __init__(self):
        self.get_node_stop_list = []
        self.route_name2 = []
        #self.counter = 0

    def get_node_stop(self, node_stop, this_route):
        self.get_node_stop_list.append(node_stop)
        self.route_name2.append(this_route)
        #self.counter = counter

    def get_nodes_stop_count(self):
        return len(self.get_node_stop_list)

    def get_first_stop(self):
        return self.get_node_stop_list[0][1]

    def get_last_stop(self):
        return self.get_node_stop_list[-1][1]

    def get_route(self):
        return self.route_name2

"""Read the list of nodes along the problematic route(s)"""
class ErrorNodeList:
    def __init__(self):
        self.node1 = []
        self.node2 = []         
        self.routeName = []     
        self.currentRoute = []  

    def get_error_nodes(self, node1, current_route):
        self.node1.append(node1)
        self.currentRoute.append(current_route)

    def check_node1(self):
        return self.node1

    def error_num_nodes(self):
        return  len(self.node1) # num of nodes, not num of pairs

    def error_route_id(self):
        return self.currentRoute


""" the list of error routes"""
class ErrorRouteList:
    def __init__(self):
        self.route_num = []
        self.route_dir = []
        self.route_direction = []
        self.route_name = []

    def get_error_route(self, counter_route, route_num, route_dir, route_direction):
        route_name = route_num + route_direction

        if route_name not in self.route_name: # when it comes to a new problematic route: self.route_name_check indexes the last (route_num + route_direction)
            self.route_num.append(route_num)
            self.route_dir.append(route_dir)
            self.route_direction.append(route_direction)
            self.route_name.append(route_name)

    def error_route(self):
        return self.route_num

    def error_dir(self):
        return self.route_dir

    def error_direction(self):
        return self.route_direction


    def error_route_name(self):
        return self.route_name
    #def error_line_direction(self):
        #return self.lineDirection

    def error_route_count(self):
        return len(self.route_name)

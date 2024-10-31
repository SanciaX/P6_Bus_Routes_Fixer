"""
Read the list of Nodes and Stops along the problematic route(s)
in case stops may be needed in future version
"""
class ErrorNodeStopList:
    def __init__(self):
        self.get_node_stop_list = [[0, 0] for _ in range(10000)]
        self.routeName2 = [0] * 10000
        self.counter = 0

    def get_node_stop(self, counter, node_stop, this_route):
        self.get_node_stop_list[counter] = node_stop
        self.routeName2[counter] = this_route
        self.counter = counter

    def get_nodes_stop_count(self):
        return self.counter

    def get_from_stop(self):
        return self.get_node_stop_list[0][1]

    def get_to_stop(self):
        return self.get_node_stop_list[self.counter][1]

    def get_route(self):
        return self.routeName2

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
        return self.counter  # numOfNodes

    def error_route_id(self):
        return self.currentRoute


""" the list of error routes"""
class ErrorRouteList:
    def __init__(self):
        self.routeNum = [0] * 100
        self.routeDir = [0] * 100
        self.routeDirection = [0] * 100
        self.routeNameCheck = 0
        self.counting1 = 0
        self.counting2 = 0

    def get_error_route(self, counter_route, route_num, route_dir, route_direction):
        if counter_route == 0:
            self.counting1 = 0
            self.routeNum[self.counting1] = route_num
            self.routeDir[self.counting1] = route_dir
            self.routeDirection[self.counting1] = route_direction
            self.routeNameCheck = route_num + route_direction

        if self.routeNameCheck != route_num + route_direction:
            self.counting1 += 1
            self.routeNum[self.counting1] = route_num
            self.routeDir[self.counting1] = route_dir
            self.routeDirection[self.counting1] = route_direction
            self.routeNameCheck = route_num + route_direction

    def error_route(self):
        return self.routeNum

    def error_dir(self):
        return self.routeDir

    def error_direction(self):
        return self.routeDirection

    #def error_line_direction(self):
        #return self.lineDirection

    def error_route_count(self):
        self.counting2 = self.counting1 + 1
        return self.counting2

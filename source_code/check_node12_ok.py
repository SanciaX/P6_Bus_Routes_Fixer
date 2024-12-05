"""Section 2.7: check if Node1, Node2 and the link in between is perfectly fine"""
class CheckNode12ok:
    def __init__(self, network_file_name_short):
        self.network_file_name_short=network_file_name_short
        self.checkNode1 = (
            []
        )  # checkNode1 is a list of Nodes that link to Node11 while Node21 has not been found to be linked to Node11
        self.check_node2 = (
            []
        )  # Nodes check_node2 is a list of Nodes that link to Node21. check_node2 would be empty if a link between Node11 & Node21 is found
        self.node11 = 0  # '10032516'
        self.node21 = 0  # '10040442'
        self.route_of_this_node = 0
        self.route_of_next_node = 0
        self.node12ok = 999  #
        self.counter = 0
    def get_error_nodes2(
        self, counter, node11, node21, route_of_this_node, route_of_next_node, nodes_check, nodes_type_check
    ):
        self.node11 = str(node11.strip())  #'10032516'
        self.node21 = str(node21.strip())  #'10040442'
        self.route_of_this_node = route_of_this_node
        self.route_of_next_node = route_of_next_node
        self.node12ok = 999  #
        with open(self.network_file_name_short, "r") as fp:
            lines = fp.readlines()
            node12ok = 0
            for line in lines:
                # check if node1 is present on a current line: if it's in, it will be added to checkNode1
                if (
                    route_of_this_node == route_of_next_node
                ):  # otherwise there is no need to search a path between node 1 and 2
                    if line.find(";B") != -1:  # check links with Bus system
                        if (
                            line.split(";")[1] == node11 and line.split(";")[2] == node21
                        ):  # when there's a link in the current network between two neighbour nodes along a line route
                            if not ((node11, node21) in nodes_check):
                                node12ok = 1
                            else:
                                type_error = nodes_type_check[nodes_check.index((node11, node21))][2]

                                if type_error == "Link Close":
                                    node12ok = 4
                                    print("Link Close:", node12ok)
                                elif type_error == "Turn block":
                                    node12ok = 5
                                    print("Turn block:", node12ok)
                                else:
                                    node12ok = -1
                                    print("Link exists but unknown Error between", node12ok)
        self.counter = counter
        self.node12ok = node12ok
        # logging.debug(f'Initialized checkNode12ok with counter: {self.counter}, node11: {self.node11}, node21: {self.node21}')
        if self.node12ok == 999:
            print("No Link between ", node12ok)
        return self.node12ok
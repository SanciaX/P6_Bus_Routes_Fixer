"""
Section 2.7: check if Node1, Node2 and the link in between is perfectly fine
self.node12ok = 999:
self.node12ok = 1:

"""
class CheckNodePairOk:
    def __init__(self, network_file_table_of_links, network_file_table_of_turns):
        self.network_file_table_of_links=network_file_table_of_links
        self.network_file_table_of_turns = network_file_table_of_turns
        self.checkNode1 = (
            []
        )  # checkNode1 is a list of Nodes that link to node01 while node02 has not been found to be linked to node01
        self.check_node2 = (
            []
        )  # Nodes check_node2 is a list of Nodes that link to node02. check_node2 would be empty if a link between node01 & node02 is found
        self.node01 = 0  # '10032516'
        self.node02 = 0  # '10040442'
        self.route_of_this_node = 0
        self.route_of_next_node = 0
        self.node12ok = 999  #
        self.counter = 0
        
    def check_nodes_errorlink(
        self, counter, node01, node02, route_of_this_node, route_of_next_node, nodes_check, nodes_type_check, error_route_mojibake
    ):
        self.node01 = str(node01.strip())  #'10032516'
        self.node02 = str(node02.strip())  #'10040442'
        self.route_of_this_node = route_of_this_node
        self.route_of_next_node = route_of_next_node
        self.node12ok = 999  # self.node12ok = 999: not yet checked
        type_error = " "
        for row in nodes_type_check:
            if row[:2] == (self.node01, self.node02):
                type_error = row[2]
        if type_error != " ":
            if type_error == "No Link":
                self.node12ok = 3  # self.node12ok = 3: there's no link between node1 and node2
                print("No Link between ", (self.node01, self.node02))
            elif type_error == "Link Close":
                self.node12ok = 4  # self.node12ok = 4: there's a closed link between node1 and node2
                print("Link Close between ", (self.node01, self.node02))
            elif type_error == "Turn block1":
                self.node12ok = 5  # self.node12ok = 5: there's a turn block between node1 and node2
                print("Turn block between ", (self.node01, self.node02))
            elif type_error == "Turn block2":
                self.node12ok = 5  # self.node12ok = 5: there's a turn block between node1 and node2
                print("Turn block between ", (self.node01, self.node02))
        else:
            with open(self.network_file_table_of_links, "r") as fp:
                lines = fp.readlines()
                for line in lines:
                    if  route_of_this_node == route_of_next_node: # otherwise there is no need to search a path between node 1 and 2
                        if line.find(";B") != -1 and  line.split(";")[1] == self.node01 and line.split(";")[2] == self.node02:  # when there's a link in the current network between two neighbour nodes along a line route and the link is open to bus mode
                            if not ((self.node01, self.node02) in nodes_check):
                                self.node12ok = 1 #self.node12ok = 1: there's a fine link between node1 and node2
                            else:
                                print("Fine link but error message between ", (self.node01, self.node02))
                                self.node12ok = 6 #self.node12ok = -1: there's a link between node1 and node2, and they are in  node12ok list, but the error type is not what I've seen before as follows
                        else:
                            self.node12ok = 7 #self.node12ok = 7: problematic link between node1 and node2 (or close to bus mode)
                            print("Problematic link (for bus) between ", (self.node01, self.node02))

        def get_nodes_errorturn(
                self, counter, node01, node02, node03,  check_route_node1, check_route_node3, nodes_check, nodes_type_check,
                error_route_mojibake
        ):
            self.node01 = str(node01.strip())
            self.node02 = str(node02.strip())
            self.node02 = str(node03.strip())
            self.check_route_node1 = check_route_node1
            self.check_route_node3 = check_route_node3
            self.node123ok = 999  #
            type_error = " "
            for row1 in nodes_type_check:
                for row2 in nodes_type_check:
                    if row1[:2] == (self.node01, self.node02) and row2[:2] == (self.node02, self.node03) :
                        type_error =  "Turn block"
                        self.node123ok = 3
            if type_error == " ":
                with open(self.network_file_table_of_turns, "r") as fp:
                    lines = fp.readlines()
                    for line in lines:
                        if check_route_node1 == check_route_node3:  # otherwise there is no need to search a path between node 1 and 2
                            if line.find(";B") != -1 and line.split(";")[0] == self.node01 and line.split(";")[
                                1] == self.node02 and line.split(";")[
                                2] == self.node03:  # when there's a link in the current network between two neighbour nodes along a line route and the link is open to bus mode
                                self.node123ok = 1  # self.node12ok = 1: there's a fine turn from node1 to node3 via node2
                            else:
                                    if  (self.node01, self.node02) in nodes_check or (self.node02, self.node03) in nodes_check:
                                        self.node123ok = 2 # self.node12ok = 2: the turn problem is due to link problem
                                    else:
                                        self.node123ok = 3 # self.node12ok = 3: problematic turn between node1 and node3
        self.counter = counter
        # logging.debug(f'Initialized CheckNodePairOk with counter: {self.counter}, node01: {self.node01}, self.node02: {self.self.node02}')
        return self.node123ok
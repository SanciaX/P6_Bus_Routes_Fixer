"""
Get the lists of Node1, Node2 on the problematic bus routes between which
the link/turn may be problematic

"""
class NodeCheckList:
    my_class_var_1 = "1"
    def __init__(self):
        self.anode1 = []
        self.anode2 = []
        self.routeName = []
        self.error_type = []

    def get_node_checklist(self, node1, node2, error_type):
        """
        :param node1: A node along (one of) the problematic bus route(s)
        :param node2: the next node after node1
        :param error_type: the type of error between node1 and node2;
         error_type is identified in Class ErrorNodes
        :return: error_type
        """
        self.anode1 = self.anode1.append(node1)
        self.anode2 = self.anode2.append(node2)
        self.error_type = self.error_type.append(error_type)

    def check_node1(self):
        return self.anode1

    def check_node2(self):
        return self.anode2

    def get_error_type(self):
        """
        :return:
        """
        return self.error_type
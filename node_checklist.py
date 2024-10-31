"""
Get the lists of Node1, Node2 on the problematic bus routes between which
the link/turn may be problematic

"""
class NodeCheckList:
    MY_CLASS_VAR_1 = "1"
    def __init__(self):
        self.anode1 = []
        self.anode2 = []
        self.routeName = []
        self.errorType = []

    def get_node_checkList(self, node1, node2, error_type):
        """
        :param node1: A node along (one of) the problematic bus route(s)
        :param node2: the next node after node1
        :param error_type: the type of error between node1 and node2;
         The errortype is identified in Class ErrorNOdes
        :return: errortype
        """
        self.anode1 = self.anode1.append(node1)
        self.anode2 = self.anode2.append(node2)
        self.errorType = self.errorType.append(error_type)

    def get_check_node1(self):
        return self.anode1

    def get_check_node2(self):
        return self.anode2

    def get_error_type(self):
        """
        :return:
        """
        return self.errorType
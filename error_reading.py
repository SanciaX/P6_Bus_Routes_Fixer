"""
Read error message and the modification causing errors
"""

class ErrorNodes:
    def __init__(self, error_message_file):
        self.errorMessageFile = error_message_file
        self.word = "Warning Line route"
        self.word1 = "Error Line route"
        self.wordTurn = ": Turn"
        self.wordTurnBlock = "is blocked for the transport system" # e.g. Error Line route 168;168 SB;>: Turn 10037016->10048187->10026747 is blocked for the transport system B.
        # link close error
        self.wordLink1 = "link"
        self.wordLink2 = " closed for the transport system B" # e.g. Error Line route 176;176 NB;>: 2 links are closed for the transport system B. Affected links: 24000455(10010348->24000154); 24000456(24000154->10053158)
        self.wordNoLinkProvide = "Error No link provided between node"
        self.wordNoLineRouteItemN = "Error No line route item was found at node"
        self.wordNoLineRouteItemS = "Error No line route item was found at stop point"
        self.wordMojibake = "Error Line route 1;1 EB;>: FORMATTING ERROR in: %1$l turns are closed for the transport system %2$s. Affected turns: %3$s"


    def read_error_file(self, error_route_list_class, node_check_list_class):
        """
        :param error_route_list_class: =ErrorRouteList(),
        will call errorRouteList_Class.get_error_route(
                    counter1, bus_route_number, bus_route_dir, direction)
        :param node_check_list_class:  =NodeCheckList()
        will call nodeCheckList_Class.get_node_checkList(node_t1, node_t2, errorType)
        :return:
        """
        with open(self.errorMessageFile, "r") as fp:
            lines = fp.readlines()

        counter1 = 0
        for line in lines:
            line = line.strip()
            if all(word in line for word in [self.word1, self.wordTurn, self.wordTurnBlock]):
                parts = line.split("->")
                node_t1 = parts[1][:8]
                node_t2 = parts[2][:8]
                node_check_list_class.get_node_checkList(node_t1, node_t2, "Turn block")

            if all(word in line for word in [self.wordLink1, self.wordLink2]):
                num_node_pair = line.count("(")
                for i in range(num_node_pair):
                    node_t1 = line.split('(')[1][0:8]
                    node_t2 = line.split('>')[1][0:8]
                    node_check_list_class.get_node_checkList(node_t1, node_t2, "Link Close")
                    line = line.split(')')[1]

            if self.wordNoLinkProvide in line:
                parts = line.split("node")
                node_t1 = parts[1][1:9]
                node_t2 = parts[2][1:9]
                node_check_list_class.get_node_checkList(node_t1, node_t2, "No Link")

            if self.word in line or self.word1 in line:
                start_index = line.find(';') + 1
                blank_string = " "
                space_index = 0
                semi_colon_index = 0
                for i in range(len(line)):
                    j = line.find(blank_string, start_index)
                    if j != -1:
                        space_index = j

                    k = line.find(";", start_index)
                    if k != -1:
                        semi_colon_index = k
                bus_route_number = line[start_index:space_index]
                bus_route_dir = line[space_index + 1:space_index + 1 + 2]
                direction = line[semi_colon_index + 1:semi_colon_index + 2]
                error_route_list_class.get_error_route(counter1, bus_route_number, bus_route_dir, direction)
                counter1 += 1


"""Recognise potential errors in the modification causing errors """
class ModificationCheckList:
    def __init__(self):
        self.links_to_check = []
        self.nodes_to_delete = []
        self.error_node_list1 = []

    def set_links_to_check(self, modification_file, error_node_list1):
        list0 = []
        nodes_delete = []
        with open(modification_file, "r") as fp:
            lines = fp.readlines()
            inside_turn_block = False
            inside_link_block = False
            for line in lines:
                line = line.strip()

                if "TURN:FROMNODENO" in line:
                    inside_turn_block = True
                    continue

                if inside_turn_block:
                    if not line:
                        inside_turn_block = False
                    elif "B," not in line:
                        parts = line.split(";")
                        if len(parts) > 2:
                            n2, n3 = int(parts[1]), int(parts[2])
                            if any(
                                    error_node_list1[i] == str(n2) and error_node_list1[i + 1] == str(n3)
                                    #errorNodeList1 is defined as errorNodeListClass.check_node1() in the main script
                                    for i in range(len(error_node_list1) - 1)
                            ):
                                list0.append([n2, n3, 5])

                if "LINK:" in line:
                    inside_link_block = True
                    continue

                if inside_link_block:
                    if not line:
                        inside_link_block = False
                    elif "B," not in line:
                        parts = line.split(";")
                        if len(parts) > 2:
                            n2, n3 = int(parts[1]), int(parts[2])
                            if any(
                                    error_node_list1[i] == str(n2) and error_node_list1[i + 1] == str(n3)
                                    for i in range(len(error_node_list1) - 1)
                            ):
                                list0.append([n2, n3, 4])

                if "Table: Nodes (deleted)" in line:
                    inside_link_block = True
                    continue

                if inside_link_block:
                    if not line:
                        inside_link_block = False
                    elif "*" not in line and "$" not in line:
                        n_missing = line
                        if any(
                                error_node_list1[i] == n_missing for i in range(len(error_node_list1) - 1)
                        ):
                            nodes_delete.append(n_missing)

        self.nodes_to_delete = nodes_delete
        self.links_to_check = list0

    def get_links_to_check(self):
        return self.links_to_check

    def get_nodes_to_delete(self):
        return self.nodes_to_delete
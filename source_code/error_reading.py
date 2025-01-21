"""
Read error message and the modification causing errors
"""

class ErrorNodes:
    def __init__(self, error_message_file):
        self.error_message_file = error_message_file
        self.word = "Warning Line route"
        self.word1 = "Error Line route"
        self.word_turn = ": Turn"
        self.word_turn_block = "is blocked for" # e.g. Error Line route 168;168 SB;>: Turn 10037016->10048187->10026747 is blocked for the transport system B.
        self.word_turn_close = "closed for"
        # link close error
        self.word_link1 = "ink"
        self.word_link_close = "closed for" # INCLUDE BOTH ONE LINK ERROR AND MULTIPLE ERRORS e.g. Error Line route 176;176 NB;>: 2 links are closed for the transport system B. Affected links: 24000455(10010348->24000154); 24000456(24000154->10053158)
        self.word_no_link_provide = "Error No link provided between node"
        self.word_no_line_route_item_node = "Error No line route item was found at node"
        self.word_no_line_route_item_stop = "Error No line route item was found at stop point"
        self.error_route_mojibake = "None"


    def read_error_file(self, error_route_list_class, node_check_list_class):
        """
        :param error_route_list_class: =ErrorRouteList(),
        will call errorRouteList_Class.get_error_route(
                    counter1, bus_route_number, bus_route_dir, direction)
        :param node_check_list_class:  =NodeCheckList()
        will call node_check_list_class.get_node_checklist(node_t1, node_t2, error_type)
        :return:
        """
        with open(self.error_message_file, "r") as fp:
            lines = fp.readlines()
        counter1 = 0
        for line in lines:
            line = line.strip()
            if all(word in line for word in [self.word_link1, self.word_link_close]):
                num_node_pair = line.count("(")
                for i in range(num_node_pair):
                    node_t1 = line.split('(')[i+1][0:8]
                    node_t2 = line.split('->')[i+1][0:8]
                    node_check_list_class.get_node_checklist(node_t1, node_t2, "Link Close, causing Turn block if there is a Turn block1 error but no Turn block2 error")

            elif self.word_no_link_provide in line:
                parts = line.split("node")
                node_t1 = parts[1][1:9]
                node_t2 = parts[2][1:9]
                node_check_list_class.get_node_checklist(node_t1, node_t2, "No Link")

            elif all(word in line for word in [self.word1, self.word_turn, self.word_turn_block]):
                parts = line.split("->")
                node_t1 = parts[0][-8:]
                node_t2 = parts[1][:8]
                node_t3 = parts[2][:8]
                node_check_list_class.get_node_checklist(node_t1, node_t2, "Turn block1")
                node_check_list_class.get_node_checklist(node_t2, node_t3, "Turn block2, possibly due to Link close")

            elif all(word in line for word in [self.word1, self.word_turn, self.word_turn_close]):
                parts = line.split("->")
                node_t1 = parts[0][-8:]
                node_t2 = parts[1][:8]
                node_t3 = parts[2][:8]
                node_check_list_class.get_node_checklist(node_t1, node_t2, "Turn close1")
                node_check_list_class.get_node_checklist(node_t2, node_t3, "Turn close2")

            # if self.word in line or self.word1 in line:
            #if '%' not in line:
            if self.word in line or self.word1 in line:
                start_index = line.find(';') + 1
                blank_string = " "
                space_index = 0
                semi_colon_index = 0
                #for i in range(len(line)):
                j = line.find(blank_string, start_index) #string.find(value, start, end)
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
            if  '%'  in line:
                self.error_route_mojibake = line.split(';')[1]
                print('Cannot identify problematic nodes, links or turns along the following route:', line)
                #THE ABOVE CODES CAN BE SHORTENED...
    def get_route_mojibake(self):
        return self.error_route_mojibake

"""Recognise potential errors from the modification causing errors """
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
                                    for i in range(len(error_node_list1) - 1)
                            ): # if n2, n3 are consecutive nodes along the error routes
                                list0.append([n2, n3, 5]) #5: turn block error

                if "LINK:" in line and "TSYSSET" in line:
                    inside_link_block = True
                    continue

                if inside_link_block:
                    if not line:
                        inside_link_block = False
                    elif "B" not in line:
                        parts = line.split(";")
                        if len(parts) > 2:
                            n2, n3 = int(parts[1]), int(parts[2])
                            if any(
                                    error_node_list1[i] == str(n2) and error_node_list1[i + 1] == str(n3)
                                    for i in range(len(error_node_list1) - 1)
                            ):
                                list0.append([n2, n3, 4])# code 4: 'link closed'

                if "Table: Links (deleted)" in line:
                    inside_link_block = True
                    continue
                if inside_link_block:
                    if not line:
                        inside_link_block = False
                    elif "*" not in line:
                        parts = line.split(";")
                        if len(parts) > 2:
                            n2, n3 = int(parts[1]), int(parts[2])
                            if any(
                                    error_node_list1[i] == str(n2) and error_node_list1[i + 1] == str(n3)
                                    for i in range(len(error_node_list1) - 1)
                            ):
                                list0.append([n2, n3, 3])# code 3: 'no link provided'

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

    def get_nodes_to_delete(self): #node(s) to be deleted from the route items
        return self.nodes_to_delete
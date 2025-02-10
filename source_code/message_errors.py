class MessageErrors:
    def __init__(self):
        self.error_list = []

    def get_errors_from_messages(self, messages):
        node_pairs = []
        line_route_keys = []
        for message in messages:
            if "No link provided between node" in message.Text:
                parts = message.Text.split(" ")
                node_no_1, node_no_2 = parts[5], parts[8].replace(".", "")
                node_pairs.append([node_no_1, node_no_2])

            elif "Line route" in message.Text and "has invalid items and is deleted" in message.Text:
                parts = message.Text.split(";")
                line_name = parts[0].split(" ")[-1]
                line_route_name = parts[1]
                line_route_direction = parts[2].split(" ")[0]
                line_route_keys.append([line_name, line_route_name, line_route_direction])
            else:
                aa = 66

        assert len(node_pairs) == len(line_route_keys)
        for node_pair, line_route_key in zip(node_pairs, line_route_keys):
            self.error_list.append(
                MessageError(
                    line_route_key[0], line_route_key[1], line_route_key[2], node_pair[0], node_pair[1]
                )
            )


class MessageError:
    def __init__(self, line_name, line_route_name, line_route_direction, node_no_1, node_no_2):
        self.line_name = line_name
        self.line_route_name = line_route_name
        self.line_route_direction = line_route_direction
        self.node_no_1 = node_no_1
        self.node_no_2 = node_no_2

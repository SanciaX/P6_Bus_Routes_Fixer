"""
This file contains functions to fix routes in Visum
"""
import logging
from pathlib import Path

class RouteFixer:
    def __init__(self):
        self.error_routes_dict = None

    def find_error_links(self, error_identifier_error_routes_dict, visum1):
        """
        Use the network of the error scenario to find problematic link(s) along error route(s)
        """
        self.error_routes_dict = error_identifier_error_routes_dict
        nodes = []
        for route_name, route_info in self.error_routes_dict.items():
            nodes = route_info.get('nodes', [])
            nodes_filtered = [node for node in nodes if node != ' ']

            # check links
            node_pair_checklist = {} # key: (node1, node2), value: True (fine link between node1 and 2)/False (error link between node1 and 2))
            for i in range(len(nodes_filtered) - 1):
                link_ok = self._check_link(visum1, nodes_filtered[i], nodes_filtered[i + 1])
                if not link_ok:
                    logging.info(f"Link Error in Route {route_name} between {nodes_filtered[i]} and {nodes_filtered[i + 1]}")
                node_pair_checklist[(nodes_filtered[i], nodes_filtered[i + 1])] = link_ok

            # check turns
            turns_ok = []
            for i in range(len(nodes_filtered) - 2):
                turn_ok = self._check_turn(visum1, nodes_filtered[i], nodes_filtered[i + 1], nodes_filtered[i + 2])
                if not turn_ok:
                    logging.info(f"Turn Error in Route {route_name} from {nodes_filtered[i]} via {nodes_filtered[i + 1]} to {nodes_filtered[i + 2]}")
                turns_ok.append([nodes_filtered[i], nodes_filtered[i + 1], nodes_filtered[i + 2], turn_ok])

                # Update node_pair_checklist based on turns_ok
                for t in range(len(turns_ok)):
                    if not turns_ok[t][3]:
                        node_pair_checklist[(turns_ok[t][0], turns_ok[t][1])] = False
                        node_pair_checklist[(turns_ok[t][1], turns_ok[t][2])] = False
            self.error_routes_dict[route_name]['link_check'] = node_pair_checklist
            # by now, self.error_routes_dict's key: route_name, value: {'nodes': nodes, 'stops': stops, 'direction_code': direction_code, 'link_check': node_pair_checklist}



    def add_routes_back(self, visum3, screenshot_taker, config):
        """
        Add fixed routes back
        """
        visum3.LoadVersion(config.error_scenario_fixing_routes_path) # scenarioErrorFixing.ver is the same as scenarioError.ver, but will have fixed routes added back later

        # For each error route
        for route_name in self.error_routes_dict:
            route_info = self.error_routes_dict[route_name]

            # For each error route, find the start and end node so that the routeitems in between will not be included when adding back this route in the next step
            start_index, end_index = self._find_start_end_nodes(route_info, route_name)

            # Add the fixed route back, ignoring the routeitems in between the start_index and end_index
            self._add_one_route_back(route_name, start_index, end_index, visum3, screenshot_taker, config)

        # Save the transfer file of adding fixed routes back
        visum3.SaveVersion(config.error_scenario_fixing_routes_path)
        visum3.GenerateModelTransferFileBetweenVersionFiles(
            config.error_scenario_path,
            config.error_scenario_fixing_routes_path,
            config.route_fixed_transfer_path,
            LayoutFile="",
            NonDefaultOnly=False,
            NonEmptyTablesOnly=True,
            WriteLayoutIntoModelTransferFile=True,
        )


    def _check_link(self, visum1, node1, node2):
        if visum1.Net.Links.LinkExistsByKey(node1, node2):
            for link in visum1.Net.Links.GetAll:
                from_node = str(int(link.AttValue("FROMNODENO")))
                to_node = str(int(link.AttValue("TONODENO")))
                tsysset = link.AttValue("TSYSSET")
                if from_node == node1 and to_node == node2 and "B" in tsysset:
                    return True
        return False


    def _check_turn(self, visum1, node1, node2, node3):
        if visum1.Net.Turns.TurnExistsByKey(node1, node2, node3):
            turn = visum1.Net.Turns.ItemByKey(node1, node2, node3)
            if "B" in turn.AttValue("TSYSSET"):
                return True
        return False


    def _find_start_end_nodes(self, route_info, route_name):
        nodes = route_info['nodes']  # including ' ', i.e. where the routeitem is a stop instead of a node
        stops = route_info['stops']  # including ' ', i.e. where the routeitem is a node instead of a stop
        node_pair_checklist = route_info['link_check']
        n_found = False
        node_before_first_error = None
        node_after_last_error = None
        node_pair_check_list = list(node_pair_checklist.items())
        for i in range(len(node_pair_check_list)):
            if not node_pair_check_list[i][1] and not n_found:  # the link in between the node_pair is erroneous
                n_found = True
                node_before_first_error = node_pair_check_list[i][0][0]  # node1 in node_pair
                break
        for i in range(len(node_pair_check_list) - 1, -1, -1):  # search reversely from the last node along this route
            if not node_pair_check_list[i][1]:  # the link in between the node_pair is erroneous
                node_after_last_error = node_pair_check_list[i][0][1]  # node2 in node_pair
                break

        if not node_before_first_error:  # if no error found
            start_index = None
            end_index = None

        if node_before_first_error:
            if not node_after_last_error:  # if the last link along the route has problem, using the last node as the end node of searching
                node_after_last_error = node_pair_check_list[-1][1]
            node_before_first_error_idx = nodes.index(
                node_before_first_error)  # index of the node before the first error along the route
            node_after_last_error_idx = nodes.index(node_after_last_error)
            search_start_node = nodes[0]  # default: search from the 1st node
            search_end_node = nodes[-1]  # default: search end at the last node
            # if start_index:
            for i in range(node_before_first_error_idx - 1, -1, -1):
                if stops[i] != ' ':  # if the route_item is a stop
                    search_start_node = nodes[
                        (i + 1)]  # search start from the node after the last stop which is before link/turn error(s)
                    break
            for i in range(node_after_last_error_idx + 1, len(nodes)):
                if stops[i] != ' ':  # if the route_item is a stop:
                    search_end_node = nodes[
                        (i - 1)]  # search ends at the node before the next stop which is after link/turn error(s)
                    break
            start_index = nodes.index(search_start_node)
            end_index = nodes.index(search_end_node)
            logging.info(f"check the route between {search_start_node} and {search_end_node} for Route {route_name}.")
        return start_index, end_index


    def _add_one_route_back(self, route_name, start_index, end_index, visum3, screenshot_taker, config):
        try:
            line = visum3.Net.Lines.ItemByKey(route_name.split(' ')[0])
            direction_code = visum3.Net.Directions.GetAll[0]
            for dirTo in visum3.Net.Directions.GetAll:
                if dirTo.AttValue("CODE") == self.error_routes_dict[route_name]['direction_code']:
                    direction_code = dirTo
            paraR1 = visum3.IO.CreateNetReadRouteSearchTSys()  # create the parameter object
            paraR1.SetAttValue("HowToHandleIncompleteRoute", 2)  # search the shortest path if line route has gaps
            paraR1.SetAttValue("ShortestPathCriterion",
                               3)  # 3:Link length; 0 Direct distance ; 1 Link travel time of current transport system; 2 Link type travel time of current transport system
            paraR1.SetAttValue("IncludeBlockedLinks", False)  # don't route over closed links
            paraR1.SetAttValue("IncludeBlockedTurns", False)  # don't route over closed turns
            paraR1.SetAttValue("MaxDeviationFactor",
                               1000)  # maximum deviation factor of shortest path search from direct distance
            paraR1.SetAttValue("WhatToDoIfShortestPathNotFound",
                               0)  # 0 Do not read ; 2 Insert link if necessary ; 1 Open link or turn for transport system

            route_items = visum3.CreateNetElements()
            node1 = None
            node2 = None
            if start_index != None:
                nodes = self.error_routes_dict[route_name]['nodes'][:(start_index + 1)] + self.error_routes_dict[route_name]['nodes'][
                                                                                     end_index:]
                node1 = self.error_routes_dict[route_name]['nodes'][(start_index + 1)]
                node2 = self.error_routes_dict[route_name]['nodes'][end_index]
                stops = self.error_routes_dict[route_name]['stops'][:(start_index + 1)] + self.error_routes_dict[route_name]['stops'][
                                                                                     end_index:]
            else:
                nodes = self.error_routes_dict[route_name]['nodes']
                stops = self.error_routes_dict[route_name]['stops']
            for i in range(len(nodes)):
                if stops[i] != ' ':
                    stop = visum3.Net.StopPoints.ItemByKey(int(stops[i]))
                    route_items.Add(stop)
                else:
                    node = visum3.Net.Nodes.ItemByKey(int(nodes[i]))
                    route_items.Add(node)

            visum3.Net.AddLineRoute(route_name, line, direction_code, route_items, paraR1)
            route = visum3.Net.LineRoutes.ItemByKey(line, direction_code, route_name)
            screenshot_taker.take_screenshot(visum3, route, Path((config.screenshot_path) / f"{route_name}-after-fixing.png"), config.afer_fixing_gpa_path, node1, node2)


        except Exception:
            logging.info(f"Not be able to generate a fixed route for route {route_name}.")

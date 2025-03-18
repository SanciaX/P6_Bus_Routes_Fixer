"""
This file contains the function that saves the fixed modifications and the fixed scenario to the Visum scenario manager.
"""
# from source_code.visum_sm_functions import add_scenario, add_modification
import shutil
import logging
from source_code.visum_connection import VisumConnection
import win32com.client
import os


class ScenarioManagementHelper:
    def __init__(self, project_path, config):
        self.visum_connection_1 = VisumConnection(25)
        self.visum_connection_2 = VisumConnection(25)
        self.visum_connection_3 = VisumConnection(25)
        self.com_constants = win32com.client.constants
        self.config = config
        self.project = self.visum_connection_1.visum.ScenarioManagement.OpenProject(project_path)
        self.working_scenario_modification_list = []
        self.error_routes_dict = {}
        self.error_scenario = None

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Closes Visum connections."""
        self.visum_connection_1.close()
        self.visum_connection_2.close()
        self.visum_connection_3.close()
        logging.info("Visum connections closed.")

    def close(self):
        self.__exit__(None, None, None)

    def read_scenario_management(self, config):
        """
        Create a new scenario containing the modifications before the error occurs and save the .ver file
        """
        error_scenario = self.visum_connection_1.visum.ScenarioManagement.CurrentProject.Scenarios.ItemByKey(config.error_scenario_id)
        old_mod_list_str = error_scenario.AttValue("MODIFICATIONS")
        mod_list = old_mod_list_str.split(',')
        self.working_scenario_modification_list = [a for a in mod_list if int(a) != int(config.error_modification_id)]
        working_mod_list = ','.join(self.working_scenario_modification_list)
        working_scenario = self.add_scenario(working_mod_list, config.scenarios_path, "Deselect the modification causing error")
        working_scenario.LoadInput()
        self.visum_connection_1.visum.SaveVersion(config.working_scenario_path)
        working_scenario.AttValue("NO")

    def save_error_routes(self):
        """
        Identify and remove erroneous routes which are recognised from the messages file.
        """
        self.visum_connection_2.visum.LoadVersion(self.config.working_scenario_path)  # visum2 links to error route instances
        self.error_scenario = self.visum_connection_1.visum.ScenarioManagement.CurrentProject.Scenarios.ItemByKey(self.config.error_scenario_id)
        self.error_scenario.LoadInput()
        line_route_key_set = set()
        for message in self.visum_connection_1.visum.Messages:
            if message.Type in [0, 1] and "Line route" in message.Text:
                parts = message.Text.split(";")
                line_name = parts[0].split(" ")[-1]
                line_route_name = parts[1]
                line_route_direction = parts[2].split(" ")[0]
                line_route_key_set.add((line_name, line_route_direction, line_route_name))

        self.visum_connection_1.visum.LoadVersion(self.config.working_scenario_path)
        for line_route_key in line_route_key_set:
            line_name, line_route_direction, line_route_name = line_route_key
            nodes, stops = ScenarioManagementHelper.get_route_items(line_name, line_route_direction, line_route_name, self.visum_connection_2)
            self.error_routes_dict[line_route_key] = {
                'nodes': nodes,
                'stops': stops
            }
            # Remove error line route from Visum_1
            route_to_remove = self.visum_connection_1.visum.Net.LineRoutes.ItemByKey(line_name, line_route_direction, line_route_name)
            self.visum_connection_1.visum.Net.RemoveLineRoute(route_to_remove)

    @staticmethod
    def get_route_items(line_name, line_route_direction, line_route_name, visum_connection):
        """Retrieves nodes and stops."""
        stops = []
        nodes = []
        lineroute = visum_connection.visum.Net.LineRoutes.ItemByKey(line_name, line_route_direction, line_route_name)
        for item in lineroute.LineRouteItems.GetAll:
            if not item.AttValue("STOPPOINTNO") and item.AttValue("NODENO"):
                stops.append(' ')
                nodes.append(str(int(item.AttValue("NODENO"))))
            elif item.AttValue("STOPPOINTNO") and not item.AttValue("NODENO"):
                stops.append(str(int(item.AttValue("STOPPOINTNO"))))
                nodes.append(' ')
        if lineroute is None:
            logging.error(f"Error retrieving route items for {line_route_name}")
        return nodes, stops

    def save_fixed_error_modification(self):
        """
        Create fixedErrorModificationFile.tra, which is a copy of the error modification but with no info. about the error routes already deleted from the network.
        This is to avoid errors that may occur when loading the error modification if the original error modification .tra contains data about error routes that are already deleted
        """
        # Delete error routes from the network before loading the modification causing errors
        self.visum_connection_1.visum.SaveVersion(self.config.working_scenario_delete_routes_path)
        # Apply the error modification with an anrController.SetWhatToDo parameter that ignore conflicting LineRouteItem data, so that when load ing the error modification, if the error modification contains data about routes just deleted, there wouldn't be error
        self.apply_model_transfer(self.visum_connection_1, self.config.error_modification_path)
        # Save the Error Scenario Model with the error routes deleted
        self.visum_connection_1.visum.SaveVersion(self.config.error_scenario_path)
        # Save the copy of the error modification that has already ignored data of already deleted error routes
        # fixedErrorModificationFile.tra is the same as the error modification except that it doesn't contain data about deleted routes
        self.visum_connection_1.visum.GenerateModelTransferFileBetweenVersionFiles(
            self.config.working_scenario_delete_routes_path,
            self.config.error_scenario_path,
            self.config.fixed_error_modification_path,
            LayoutFile="",
            NonDefaultOnly=False,
            NonEmptyTablesOnly=True,
            WriteLayoutIntoModelTransferFile=True,
        )

        # Save scenarioErrorFixing.ver (where we add routes back) so that we can get fixedRouteAddedTransfer.tra by comparing scenarioErrorFixing.ver against scenarioError.ver
        # error_scenario_path being the error scenario without error routes; error_scenario_fixing_routes_path being the scenario with fixed routes added back
        shutil.copy2(self.config.error_scenario_path, self.config.error_scenario_fixing_routes_path)

    def save_the_routes_deleting_ver(self):
        """
        Create a transfer file of deleting error routes
        """
        self.visum_connection_1.visum.GenerateModelTransferFileBetweenVersionFiles(
            self.config.working_scenario_path,
            self.config.working_scenario_delete_routes_path,
            self.config.route_deleted_transfer_path,
            LayoutFile="",
            NonDefaultOnly=False,
            NonEmptyTablesOnly=True,
            WriteLayoutIntoModelTransferFile=True,
        )
        # Create a new modification in Scenario Management which deletes error routes (i.e. apply routeDeletedTransfer.tra)
        modification1, mod_delete_routes_path, mod_delete_routes_name, mod_delete_routes_id = self.add_modification(
            "Erroneous Routes Deleted",
            "Copied from the last working modification and have problematic routes deleted"
        )
        shutil.copy2(self.config.route_deleted_transfer_path, mod_delete_routes_path)

    def save_to_scenario_manager(self, new_mode_list):
        # generate a modification that deletes the problematic routes
        code = "Delete Problematic Routes for Scenario " + self.config.error_scenario_id_str
        modification2, mod2_path, mode2_name, mode2_id = self.add_modification(code, "Delete problematic routes")
        path_str = self.config.route_deleted_transfer_path.as_posix()
        shutil.copy2(path_str, mod2_path)

        # generate a modification that is copied from the error modification but ignores data about the problematic routes
        code = "Add the Modification that Resulted in Errors Back " + self.config.error_scenario_id_str
        modification3, mod3_path, mode3_name, mode3_id = self.add_modification(code, "With no info. about deleted error routes")
        path_str = self.config.fixed_error_modification_path.as_posix()
        shutil.copy2(path_str, mod3_path)

        # generate a modification that adds the fixed routes
        modification4, mod4_path, mode4_name, mode4_id = self.add_modification("Problematic Routes Re-added", "Have the deleted problematic routes fixed and re-added to the erroneous scenario's network")
        path_str = self.config.route_fixed_transfer_path.as_posix()
        shutil.copy2(path_str, mod4_path)
        final_mod_list_str = ",".join(new_mode_list + list(map(str, [mode2_id, mode3_id, mode4_id])))
        logging.info("The scenario fixed has the following modifications: " + final_mod_list_str)
        code = "Bus Route Fixed for Scenario " + self.config.error_scenario_id_str
        cur_scenario = self.add_scenario(final_mod_list_str, self.config.scenarios_path, code)
        cur_scenario.LoadInput()
        self.project.RemoveScenario(cur_scenario.AttValue("NO")-1)

    def add_scenario(self, modifications, scenarios_path, code):
        new_scenario = self.project.AddScenario()
        new_scenario_id = new_scenario.AttValue("NO")
        new_scenario.SetAttValue("CODE", code)
        new_scenario.SetAttValue("PARAMETERSET", "1")
        new_scenario.SetAttValue("MODIFICATIONS", modifications)
        new_scenario_folder = f"S{str(int(new_scenario_id)).zfill(6)}"
        error_message_path_working = scenarios_path / new_scenario_folder / 'Messages.txt'
        self.visum_connection_1.visum.SetErrorFile(error_message_path_working)
        return new_scenario

    def add_modification(self, code, description):
        new_modification = self.project.AddModification()
        new_modification.SetAttValue("Code", code)
        new_modification.SetAttValue("Description", description)
        new_mode_id = int(new_modification.AttValue("No"))
        mod_name = new_modification.AttValue("TraFile")
        str_path = self.config.scenario_management_base_path.as_posix()
        mod_path = os.path.join(str_path, "Modifications", mod_name)
        return new_modification, mod_path, mod_name, new_mode_id

    @staticmethod
    def apply_model_transfer(visum_connection, tra_path):
        win32com_constants = win32com.client.constants
        anrController = visum_connection.visum.IO.CreateAddNetReadController()
        anrController.SetWhatToDo("Line", win32com_constants.AddNetRead_OverWrite)
        anrController.SetWhatToDo("LineRoute", win32com_constants.AddNetRead_Ignore)
        anrController.SetWhatToDo("LineRouteItem", win32com_constants.AddNetRead_Ignore)
        anrController.SetWhatToDo("TimeProfile", win32com_constants.AddNetRead_Ignore)
        anrController.SetWhatToDo("TimeProfileItem", win32com_constants.AddNetRead_Ignore)
        anrController.SetWhatToDo("VehJourney", win32com_constants.AddNetRead_Ignore)
        anrController.SetUseNumericOffset("VehJourney", True)
        anrController.SetWhatToDo("VehJourneyItem", win32com_constants.AddNetRead_DoNothing)
        anrController.SetWhatToDo("VehJourneySection", win32com_constants.AddNetRead_Ignore)
        anrController.SetWhatToDo("ChainedUpVehJourneySection", win32com_constants.AddNetRead_DoNothing)
        anrController.SetWhatToDo("UserAttDef", win32com_constants.AddNetRead_Ignore)
        anrController.SetWhatToDo("Operator", win32com_constants.AddNetRead_OverWrite)
        anrController.SetConflictAvoidingForAll(10000, "ORG_")
        visum_connection.visum.ApplyModelTransferFile(tra_path, anrController)

    def find_error_links(self):
        """
        Use the network of the error scenario to find problematic link(s) along error route(s)
        """
        #self.error_routes_dict = error_identifier_error_routes_dict
        for route_name, route_info in self.error_routes_dict.items():
            nodes = route_info.get('nodes', [])
            nodes_filtered = [node for node in nodes if node != ' ']

            # check links
            node_pair_checklist = {} # key: (node1, node2), value: True (fine link between node1 and 2)/False (error link between node1 and 2))
            for node1, node2 in zip(nodes_filtered, nodes_filtered[1:]):
                link_ok = self._check_link(self.visum_connection_1, node1, node2)
                if not link_ok:
                    logging.info(f"Link Error in Route {route_name} between {node1} and {node2}")
                node_pair_checklist[(node1, node2)] = link_ok

            # Check turns
            turns_ok = []
            for node1, node2, node3 in zip(nodes_filtered, nodes_filtered[1:], nodes_filtered[2:]):
                turn_ok = self._check_turn(self.visum_connection_1, node1, node2, node3)
                if not turn_ok:
                    logging.info(f"Turn Error in Route {route_name} from {node1} via {node2} to {node3}")
                turns_ok.append([node1, node2, node3, turn_ok])

            # Update node_pair_checklist based on turns_ok
            for node1, node2, node3, turn_ok in turns_ok:
                if not turn_ok:
                    node_pair_checklist[(node1, node2)] = False
                    node_pair_checklist[(node2, node3)] = False
            self.error_routes_dict[route_name]['link_check'] = node_pair_checklist

    def _check_link(self, visum_connection, node1, node2):
        if visum_connection.visum.Net.Links.LinkExistsByKey(node1, node2):
            link = visum_connection.visum.Net.Links.ItemByKey(node1, node2)
            from_node = str(int(link.AttValue("FROMNODENO")))
            to_node = str(int(link.AttValue("TONODENO")))
            tsysset = link.AttValue("TSYSSET")
            if from_node == node1 and to_node == node2 and "B" in tsysset:
                return True
        return False

    def _check_turn(self, visum_connection, node1, node2, node3):
        if visum_connection.visum.Net.Turns.TurnExistsByKey(node1, node2, node3):
            turn = visum_connection.visum.Net.Turns.ItemByKey(node1, node2, node3)
            if "B" in turn.AttValue("TSYSSET"):
                return True
        return False

    def add_routes_back(self):
        """
        Add fixed routes back
        """
        self.visum_connection_3.visum.LoadVersion(self.config.error_scenario_fixing_routes_path) # scenarioErrorFixing.ver is the same as scenarioError.ver, but will have fixed routes added back later

        # For each error route
        for route_name, route_info in self.error_routes_dict.items():
            route_info = self.error_routes_dict[route_name]

            # For each error route, find the start and end node so that the linerouteitems in between will not be included when adding back this route in the next step
            start_index, end_index = self._find_start_end_nodes(route_info, route_name)

            # Add the fixed route back, ignoring the LineRouteItems in between the start_index and end_index
            self._add_one_route_back(route_name, start_index, end_index, self.visum_connection_3.visum)

        # Save the transfer file of adding fixed routes back
        self.visum_connection_3.visum.SaveVersion(self.config.error_scenario_fixing_routes_path)
        self.visum_connection_3.visum.GenerateModelTransferFileBetweenVersionFiles(
            self.config.error_scenario_path,
            self.config.error_scenario_fixing_routes_path,
            self.config.route_fixed_transfer_path,
            LayoutFile="",
            NonDefaultOnly=False,
            NonEmptyTablesOnly=True,
            WriteLayoutIntoModelTransferFile=True,
        )

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
                    # search start from the node after the last stop which is before link/turn error(s)
                    search_start_node = nodes[(i + 1)]
                    break
            for i in range(node_after_last_error_idx + 1, len(nodes)):
                if stops[i] != ' ':  # if the route_item is a stop:
                    # search ends at the node before the next stop which is after link/turn error(s)
                    search_end_node = nodes[(i - 1)]
                    break
            start_index = nodes.index(search_start_node)
            end_index = nodes.index(search_end_node)
            logging.info(f"check the route between {search_start_node} and {search_end_node} for LineRoute {route_name}.")
        else:
            start_index = None
            end_index = None
        return start_index, end_index

    def _add_one_route_back(self, route_name, start_index, end_index, visum3):
        try:
            line = visum3.Net.Lines.ItemByKey(route_name.split(' ')[0])
            direction_code = visum3.Net.Directions.GetAll[0]
            for dirTo in visum3.Net.Directions.GetAll:
                if dirTo.AttValue("CODE") == self.error_routes_dict[route_name]['direction_code']:
                    direction_code = dirTo
            paraR1 = visum3.IO.CreateNetReadRouteSearchTSys()  # create the parameter object
            paraR1.SetAttValue("HowToHandleIncompleteRoute", 2)  # search the shortest path if line route has gaps
            paraR1.SetAttValue("ShortestPathCriterion", 3)  # 3:Link length; 0 Direct distance ; 1 Link travel time of current transport system; 2 Link type travel time of current transport system
            paraR1.SetAttValue("IncludeBlockedLinks", False)  # don't route over closed links
            paraR1.SetAttValue("IncludeBlockedTurns", False)  # don't route over closed turns
            paraR1.SetAttValue("MaxDeviationFactor", 1000)  # maximum deviation factor of shortest path search from direct distance
            paraR1.SetAttValue("WhatToDoIfShortestPathNotFound", 0)  # 0 Do not read ; 2 Insert link if necessary ; 1 Open link or turn for transport system

            route_items = visum3.CreateNetElements()
            if start_index != None:
                nodes = self.error_routes_dict[route_name]['nodes'][:(start_index + 1)] + self.error_routes_dict[route_name]['nodes'][
                                                                                     end_index:]
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

        except Exception:
            logging.info(f"Not be able to generate a fixed route for route {route_name}.")


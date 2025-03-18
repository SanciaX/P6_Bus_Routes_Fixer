"""
This file contains the function that saves the fixed modifications and the fixed scenario to the Visum scenario manager.
"""
from source_code.visum_sm_functions import add_scenario, add_modification
import shutil
import logging


class ScenarioManagementHelper:
    def __init__(self):
        self.project = 1

    def save_to_scenario_manager(self, this_project, config, new_mode_list, visum1):

        # generate a modification that deletes the problematic routes
        code = "Delete Problematic Routes for Scenario " + config.error_scenario_id_str
        modification2, mod2_path, mode2_name, mode2_id = add_modification(this_project, config, code,
                                                             "Delete problematic routes")
        path_str = config.route_deleted_transfer_path.as_posix()
        shutil.copy2(path_str, mod2_path)

        # generate a modification that is copied from the error modification but ignores data about the problematic routes
        code = "Add the Modification that Resulted in Errors Back " + config.error_scenario_id_str
        modification3, mod3_path, mode3_name, mode3_id = add_modification(this_project, config, code, "With no info. about deleted error routes")
        path_str = config.fixed_error_modification_path.as_posix()
        shutil.copy2(path_str, mod3_path)

        # generate a modification that adds the fixed routes
        modification4, mod4_path, mode4_name, mode4_id = add_modification(this_project, config,"Problematic Routes Re-added", "Have the deleted problematic routes fixed and re-added to the erroneous scenario's network")
        path_str = config.route_fixed_transfer_path.as_posix()
        shutil.copy2(path_str, mod4_path)
        final_mod_list_str = ",".join(new_mode_list + list(map(str, [mode2_id, mode3_id, mode4_id])))
        logging.info("The scenario fixed has the following modifications: " + final_mod_list_str)
        code = "Bus Route Fixed for Scenario " + config.error_scenario_id_str
        cur_scenario = add_scenario(visum1, this_project, final_mod_list_str, config.scenarios_path,code)
        cur_scenario.LoadInput()
        this_project.RemoveScenario(cur_scenario.AttValue("NO")-1)

    def add_scenario(self, project, modifications, scenarios_path, code):
        new_scenario = project.AddScenario()
        new_scenario_id = new_scenario.AttValue("NO")
        new_scenario.SetAttValue("CODE", code)
        new_scenario.SetAttValue("PARAMETERSET", "1")
        new_scenario.SetAttValue("MODIFICATIONS", modifications)
        new_scenario_folder = f"S{str(int(new_scenario_id)).zfill(6)}"
        error_message_path_working = scenarios_path / new_scenario_folder / 'Messages.txt'
        visum.SetErrorFile(error_message_path_working)
        return new_scenario

    def add_modification(project, config, code, description):
        new_modification = project.AddModification()
        new_modification.SetAttValue("Code", code)
        new_modification.SetAttValue(
            "Description", description
        )
        new_mode_id = int(new_modification.AttValue("No"))
        mod_name = new_modification.AttValue("TraFile")
        str_path = str(config.scenario_management_base_path).replace('/', '\\\\')
        mod_path = (
                str_path
                + "\\Modifications\\" + mod_name
        )
        return new_modification, mod_path, mod_name, new_mode_id

    def apply_model_transfer(visum, tra_path):
        win32com_constants = win32com.client.constants
        anrController = visum.IO.CreateAddNetReadController()
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
        visum.ApplyModelTransferFile(tra_path, anrController)

    def get_route_items(route_name, visum):
        """Retrieves nodes and stops."""
        lineroute = None
        nodes = []
        stops = []
        try:
            for r in visum.Net.LineRoutes.GetAll:
                if r.AttValue("NAME") == route_name:
                    lineroute = r
            for item in lineroute.LineRouteItems.GetAll:
                if not item.AttValue("STOPPOINTNO") and item.AttValue("NODENO"):
                    stops.append(' ')
                    nodes.append(str(int(item.AttValue("NODENO"))))
                elif item.AttValue("STOPPOINTNO") and not item.AttValue("NODENO"):
                    stops.append(str(int(item.AttValue("STOPPOINTNO"))))
                    nodes.append(' ')
            if lineroute is None:
                logging.error(f"Error retrieving route items for {route_name}")
        except Exception:
            pass
        return nodes, stops

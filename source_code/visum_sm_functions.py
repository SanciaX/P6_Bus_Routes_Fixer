"""
This module contains functions to interact with PTV Visum Scenario Management.
"""
import win32com.client
import logging


def add_scenario(visum, project, modifications, scenarios_path, code):
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


def get_route_items(route_name,visum):
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

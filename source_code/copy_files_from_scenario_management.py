import win32com.client

def copy_files_from_scenario_management(
        this_project, error_scenario_id, error_message_dir,
        working_scenario_name, network_file_name, error_message_log
):

    # Create a new scenario containing the modifications before the error occurs and save the .ver file
    error_scenario = Visum.ScenarioManagement.CurrentProject.Scenarios.ItemByKey(error_scenario_id)
    old_mod_set = error_scenario.AttValue("MODIFICATIONS")
    working_mod_set = old_mod_set[:-1]

    working_scenario = this_project.AddScenario()
    working_scenario_id = working_scenario.AttValue("NO")
    working_scenario.SetAttValue("CODE", "BusRouteFixed")
    working_scenario.SetAttValue("PARAMETERSET", "1")
    working_scenario.SetAttValue("MODIFICATIONS", working_mod_set)

    error_message_file_working = error_message_dir + str(working_scenario_id) + ".txt"
    Visum.SetErrorFile(error_message_file_working)
    working_scenario.LoadInput()
    Visum.SaveVersion(working_scenario_name)

    error_scenario.LoadInput()
    Visum.IO.SaveNet(
        network_file_name,
        LayoutFile="",
        EditableOnly=True,
        NonDefaultOnly=True,
        ActiveNetElemsOnly=False,
        NonEmptyTablesOnly=True,
    )
    Visum.SetErrorFile(error_message_log)
    return (
    error_scenario, old_mod_set, working_mod_set, working_scenario, working_scenario_id, error_message_file_working)
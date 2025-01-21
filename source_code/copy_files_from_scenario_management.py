import win32com.client

def copy_files_from_scenario_management(Visum,
        this_project, error_scenario_id, scenarios_path,
        working_scenario_name, error_scenario_network_file_name, error_message_log
):

    # Create a new scenario containing the modifications before the error occurs and save the .ver file
    error_scenario = Visum.ScenarioManagement.CurrentProject.Scenarios.ItemByKey(error_scenario_id)
    old_mod_set = error_scenario.AttValue("MODIFICATIONS")
    mod_list = old_mod_set.split(',')
    working_mod_set = ','.join(mod_list[:-1])

    working_scenario = this_project.AddScenario() # Add a new scenario with all the modifications before the error occurs
    working_scenario_id = working_scenario.AttValue("NO")
    working_scenario.SetAttValue("CODE", "BusRouteFixed")
    working_scenario.SetAttValue("PARAMETERSET", "1")
    working_scenario.SetAttValue("MODIFICATIONS", working_mod_set)
    working_scenario_path = 'S000000'[:-len(str(int(working_scenario_id)))] + str(int(working_scenario_id))
    error_message_file_working =  scenarios_path / working_scenario_path / 'Messages.txt'
    Visum.SetErrorFile(error_message_file_working)
    working_scenario.LoadInput()
    Visum.SaveVersion(working_scenario_name)

    error_scenario.LoadInput()
    Visum.IO.SaveNet(
        error_scenario_network_file_name,
        LayoutFile="",
        EditableOnly=True,
        NonDefaultOnly=True,
        ActiveNetElemsOnly=False,
        NonEmptyTablesOnly=True,
    )
    Visum.SetErrorFile(error_message_log)
    return old_mod_set, error_message_file_working
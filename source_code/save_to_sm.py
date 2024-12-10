# source_code/save_to_sm.py

# new error_modification
import shutil

def save_to_sm(this_project, error_mod_transfer_file, route_added_transfer_file_final, old_mod_set, new_mod_no1, error_message_dir, Visum):
    # new error_modification
    new_modification = this_project.AddModification()
    new_modification.SetAttValue("Code", "Refined Problematic Modification")
    new_modification.SetAttValue(
        "Description",
        "Copied from the modification with error, with the erroreous modiffication reloaded using conflict avoiding parameters",
    )
    new_mod_no2 = int(new_modification.AttValue("No"))
    this_mod_name2 = new_modification.AttValue("TraFile")
    mod_file_name2 = (
        "C:\\Users\\Shanshan Xie\\TfL\\06 Scenario management\\SM_TESTING\\Modifications\\"
        + this_mod_name2
    )
    shutil.copy2(error_mod_transfer_file, mod_file_name2)  # to keep the start file unchanged

    # add the fixed routes
    new_modification = this_project.AddModification()
    new_modification.SetAttValue("Code", "Problematic Routes Re-added")
    new_modification.SetAttValue("Description", "Have the deleted problematic routes added")
    new_mod_no3 = int(new_modification.AttValue("No"))
    this_mod_name3 = new_modification.AttValue("TraFile")

    mod_file_name3 = (
        "C:\\Users\\Shanshan Xie\\TfL\\06 Scenario management\\SM_TESTING\\Modifications\\"
        + this_mod_name3
    )
    shutil.copy2(route_added_transfer_file_final, mod_file_name3)  # to keep the start file unchanged

    # apply the Modification with error
    new_mod_set = old_mod_set[:-1] + str(new_mod_no1) + "," + str(new_mod_no2) + "," + str(new_mod_no3)
    print(new_mod_set)
    cur_scenario = this_project.AddScenario()
    cur_scenario_id = cur_scenario.AttValue("NO")
    cur_scenario.SetAttValue("CODE", "BusRouteFixed")
    cur_scenario.SetAttValue("PARAMETERSET", "1")
    cur_scenario.SetAttValue("MODIFICATIONS", new_mod_set)
    error_message_file_fixed = error_message_dir + str(cur_scenario_id) + ".txt"  # new error file
    Visum.SetErrorFile(error_message_file_fixed)  # writing error message on a defined file
    cur_scenario.LoadInput()

    return new_mod_no2, this_mod_name2, mod_file_name2, new_mod_no3, this_mod_name3, mod_file_name3, new_mod_set, cur_scenario_id, error_message_file_fixed
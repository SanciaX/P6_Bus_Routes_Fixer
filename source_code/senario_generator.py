"""
This file contains the function that saves the fixed modifications and the fixed scenario to the Visum scenario manager.
"""

from visum_sm_functions import add_scenario, add_modification
import shutil
import logging

class ScenarioGenerator:
    def save_to_sm(self, this_project, config, new_mode_set, visum1):

        # generate a modification that deletes the problematic routes
        code = "Delete Problematic Routes for Scenario " + config.error_scenario_id_str
        modification2, mod2_path, mode2_name, mode2_id = add_modification(this_project, config, code,
                                                             "Delete problematic routes")
        path_str = str(config.route_deleted_transfer_path).replace('/', '\\\\')
        shutil.copy2(path_str, mod2_path)

        # generate a modification that is copied from the error modification but ignores data about the problematic routes
        code = "Add the Modification that Resulted in Errors Back " + config.error_scenario_id_str
        modification3, mod3_path, mode3_name, mode3_id = add_modification(this_project, config, code, "With no info. about deleted error routes")
        path_str = str(config.fixed_error_modification_path).replace('/', '\\\\')
        shutil.copy2(path_str, mod3_path)

        # generate a modification that adds the fixed routes
        modification4, mod4_path, mode4_name, mode4_id = add_modification(this_project, config,"Problematic Routes Re-added", "Have the deleted problematic routes fixed and re-added to the erroneous scenario's network")
        path_str = str(config.route_fixed_transfer_path).replace('/', '\\\\')
        shutil.copy2(path_str, mod4_path)
        mode_set_str = ''
        for mod in new_mode_set:
            mode_set_str += mod + ","
        final_mod_set = mode_set_str  + str(mode2_id) + "," + str(mode3_id) + "," + str(mode4_id)
        logging.info("The scenario fixed has the following modifications: " + final_mod_set)
        code = "Bus Route Fixed for Scenario " + config.error_scenario_id_str
        cur_scenario = add_scenario(visum1, this_project, final_mod_set, config.scenarios_path,code)
        cur_scenario.LoadInput()
        this_project.RemoveScenario(cur_scenario.AttValue("NO")-1)

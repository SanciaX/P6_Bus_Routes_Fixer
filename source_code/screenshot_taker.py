
from visum_sm_functions import add_scenario

class ScreenshotTaker:

    def take_screenshot_in_modification(self, visum, route, config):
        scenarios_path = config.scenarios_path
        screenshotpath = config.screenshotpath
        error_modification = int(config.error_scenario_id)
        scenario_last = visum.ScenarioManagement.CurrentProject.Scenarios.GetAll[-1]
        scenario_errormodification_only = add_scenario(visum, error_modification, scenarios_path)
        scenario_errormodification_only.LoadInput()
        self.take_screenshot(visum, route, screenshotpath, config.error_modification_gpa_path)
        scenario_last.LoadInput()
        visum.ScenarioManagement.CurrentProject.RemoveScenario(scenario_errormodification_only)

    def take_screenshot(self, visum, route, screenshotpath, gpa_path, node1=None, node2=None):
        """Takes a screenshot of the bus route."""
        # bus_route_fixer.gpa: show activate bus route(s) only; show marked nodes.
        visum.Net.GraphicParameters.Open(gpa_path)
        visum.Graphic.Autozoom(route)
        for r in visum.Net.LineRoutes.GetAll:
            if r.AttValue("NAME") != route.AttValue("NAME"):
                r.Active = False
            else:
                r.Active = True
        if node1 and node2:
            n1 = visum.Net.Nodes.ItemByKey(int(node1))
            n2 = visum.Net.Nodes.ItemByKey(int(node2))
            visum.Net.Marking.ObjectType = 1
            visum.Net.Marking.Add(n1)
            visum.Net.Marking.Add(n2)

        visum.Graphic.Screenshot(screenshotpath, ScreenResFactor=1)
        visum.Net.Marking.Clear
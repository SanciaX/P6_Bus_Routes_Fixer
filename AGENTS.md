# AGENTS.md

## Scope and Goal
- This project fixes bus route conflicts inside PTV Visum Scenario Management by rebuilding only problematic line-route segments, while preserving non-route network changes (`bus_routes_fixer/bus_routes_fixer.py`).
- Main entrypoint for normal runs: `python -m bus_routes_fixer.user_run_scripts.user_run` (see `README.md`).

## Architecture Map (read these first)
- `bus_routes_fixer/bus_routes_fixer.py`: Orchestrator (`BusRoutesFixer.run_fixer`) that runs the full pipeline.
- `bus_routes_fixer/directory_config.py`: Singleton config loader + runtime path builder + startup cleanup of temp/screenshot folders.
- `bus_routes_fixer/scenario_management_helper.py`: Core domain logic (scenario splitting, route deletion, shortest-path-based route rebuild, transfer file generation, scenario/modification creation).
- `bus_routes_fixer/visum_connection.py`: COM bootstrap for Visum (`win32com.client.gencache.EnsureDispatch`).
- `bus_routes_fixer/logger_configuration.py`: File + console logging setup under `bus_routes_fixer/outputs/log`.

## End-to-End Data Flow
1. Read error scenario and split modifications into pre-error vs from-first-error lists (`read_scenario_management`).
2. Detect error routes from Visum messages containing `"Line route"`; cache nodes/stops; remove those routes (`save_error_routes`).
3. Build "fixed" copies of modifications by applying transfers while ignoring line-route tables (`apply_model_transfer` ignores `LineRoute`, `LineRouteItem`, `TimeProfile`, etc.).
4. Identify broken route sections by link/turn checks with bus transport system `B` (`_check_link`, `_check_turn`).
5. Re-add each route with shortest-path gap handling (`_add_each_route_back`, `HowToHandleIncompleteRoute=2`), then export transfer files.
6. Create new scenario-management modifications and final fixed scenario (`save_to_scenario_manager`).

## Critical Workflows
- Environment bootstrap (Windows-focused): `python setup_env.py` (`setup_env.py` creates `.venv` and installs `requirements.txt`).
- Required config before running: `bus_routes_fixer/config/directories.json` (`error_scenario_id`, `id_of_the_1st_error_modification`, scenario paths, `visum_version`).
- Profiling run is built in: `bus_routes_fixer/user_run_scripts/user_run.py` wraps `main()` with `cProfile` and prints top 50 hot spots.
- Manual verification outputs are expected artifacts: screenshots in `bus_routes_fixer/outputs/bus_routes_screenshots` and logs in `bus_routes_fixer/outputs/log`.

## Project-Specific Conventions and Risks
- `DirectoryConfig` is a singleton; avoid assumptions that re-instantiating it reloads changed JSON in the same process.
- Startup is destructive for generated artifacts: `directory_config.py` clears screenshot and temp folders each run.
- Bus route internals encode route sequences with placeholders: `' '` marks node-vs-stop positions (`get_route_items`). Preserve this format when editing route logic.
- The code currently hardcodes `VisumConnection(26)` in `ScenarioManagementHelper.__init__` rather than using `config.visum_version`; account for this before version-related changes.
- Scenario/modification IDs are string-zero-padded (e.g., `M000005`, `S000014`) and used to build file paths; keep this formatting consistent.

## Integration Points
- External dependency is COM automation against installed PTV Visum (`pywin32`, `win32com.client`); this cannot be fully tested in a generic CI environment.
- Transfer files (`*.tra`) and version files (`*.ver`) are primary interchange artifacts between steps; many functions assume these files exist from prior pipeline stages.
- GPA resources used for screenshots live in `bus_routes_fixer/resources/*.gpa`; screenshot steps depend on those files being present.

## When Making Changes
- Prefer small edits in `scenario_management_helper.py`; many methods rely on side effects from previous pipeline steps.
- Validate by running against a known scenario and checking both generated modifications and screenshot/log outputs, not just Python execution success.
- If adding tests, isolate pure helpers first (`_merge_close_nodes`, `_find_error_bus_stop_pairs`) since COM-heavy methods require Visum runtime.


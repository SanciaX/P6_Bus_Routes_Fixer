import os
import logging
from datetime import datetime


def setup_logger():
    log_directory = os.path.join(os.getcwd(), 'bus_routes_fixer', 'outputs', 'log')
    # Check if the directory exists, and create it if it does not
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    logging.basicConfig(
        filename=f"bus_routes_fixer/outputs/log/{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}_bus_routes_fixer.log",
        level=logging.INFO,
        format="[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    # set up logging to console
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    # set a format which is simpler for console use
    formatter = logging.Formatter("%(name)-12s: %(levelname)-8s %(message)s")
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger("").addHandler(console)
    return logging.getLogger(__name__)

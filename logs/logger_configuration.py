# Configure logging
# File paths for logs
import logging


from user_inputs import *

debug_log_path = bus_routes_fix_path+ r"\debug.log"
derived_data_log_path = bus_routes_fix_path+r"\Notes_for_Visum_Modeller.log"

# Configure logger for debugging messages
debug_logger = logging.getLogger("debug_logger")
debug_logger.setLevel(logging.DEBUG)

debug_handler = logging.FileHandler(debug_log_path)
debug_handler.setLevel(logging.DEBUG)
debug_format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
debug_handler.setFormatter(debug_format)

debug_logger.addHandler(debug_handler)

# Configure logger for derived data
data_logger = logging.getLogger("data_logger")
data_logger.setLevel(logging.INFO)

data_handler = logging.FileHandler(derived_data_log_path)
data_handler.setLevel(logging.INFO)
data_format = logging.Formatter("%(message)s")
data_handler.setFormatter(data_format)

data_logger.addHandler(data_handler)

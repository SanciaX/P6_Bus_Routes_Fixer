import win32com.client
import logging
import os
import shutil


class VisumConnection:
    """Manages connections to PTV Visum."""
    def __init__(self, visum_version):
        self.visum_version = visum_version
        self.visum = None
        self.connect()

    def connect(self):
        """Connects to Visum."""
        try:
            # First try with EnsureDispatch
            try:
                self.visum = win32com.client.gencache.EnsureDispatch(f"Visum.Visum.{self.visum_version}")
                logging.info(f"PTV Visum started using EnsureDispatch: {self.visum}")
            except Exception as e:
                logging.warning(f"EnsureDispatch failed: {e}")

                # Clear gen_py cache and retry
                self.clear_cache()
                self.visum = win32com.client.gencache.EnsureDispatch(f"Visum.Visum.{self.visum_version}")
                logging.info(f"After clearing the gen_py cache, PTV Visum started using EnsureDispatch: {self.visum}")

        except Exception as e:
            logging.error(f"Error connecting to Visum: {e}")
            raise

    def __exit__(self):
        self.close()

    def close(self):
        """Closes the Visum connection."""
        if self.visum:
            self.visum = None
            logging.info("Visum connection closed.")

    @staticmethod
    def clear_cache():
        cache_path = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "gen_py")
        if os.path.exists(cache_path):
            shutil.rmtree(cache_path)

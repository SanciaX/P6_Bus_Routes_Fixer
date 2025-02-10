import json
import os


class ConfigLoader:
    def __init__(self, **kwargs):
        # Dynamically set class attributes from kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.__dict__})"

    @classmethod
    def from_config_path(cls, file_path: str):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Config file not found: {file_path}")
        with open(file_path, 'r') as file:
            config_data = json.load(file)
        return cls(**config_data)


if __name__ == "__main__":
    config_path = "config/directories.json"
    config = ConfigLoader.from_config_path(config_path)
    print(config)

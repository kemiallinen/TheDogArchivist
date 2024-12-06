import json
import os

class Config:
    def __init__(self, config_file="app/config/config.json"):
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self):
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"Config file '{self.config_file}' not found.")
        with open(self.config_file, "r") as file:
            return json.load(file)

    def get(self, key, default=None):
        keys = key.split(".")
        value = self.config
        for k in keys:
            if k in value:
                value = value[k]
            else:
                return default
        return value

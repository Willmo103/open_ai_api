import json
import os


class Globals():

    _path: str = os.path.dirname(__file__) + os.path.sep + "globals.json"

    def __init__(self):

        if not os.path.exists(self._path):
            self._create_globals()

        with open(self._path, "r") as f:
            data = json.load(f)
        self.ignore = data["ignore"]
        self.API_KEY = data["API_KEY"]
        self.ORG_KEY = data["ORG_KEY"]
        self.models = data["models"]

    def __repr__(self) -> str:
        return f"Globals(ignore={self.ignore} API_KEY=HIDDEN, ORG_KEY=HIDDEN)"

    def _create_globals(self, path):

        # get the root install path to generate/look for globals.json


        # keys is a list of all the keys that need to be present in the json object
        keys: list = ["ignore", "API_KEY", "ORG_KEY"]
        defaults: dict = {"ignore": []}

        # read the object make sure all keys are present
        try:
            with open(self._path, "r") as f:
                data = json.load(f)
            assert all(key in data for key in keys)
            return
        except (FileNotFoundError, json.JSONDecodeError):
            print("No globals.json file found, generating globals.json...")
            data = defaults.copy()
            data["API_KEY"] = input("Enter your openai API key: 'sk-...'\n> ")
            data["ORG_KEY"] = input("Enter your openai ORG key: 'org-...'\n> ")

            with open(self._path, "w") as f:
                json.dump(data, f, indent=4)

            print("globals saved")
            return

globals = Globals()




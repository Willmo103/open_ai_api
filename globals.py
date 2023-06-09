import json
import os
import openai


class Globals:

    _path: str = os.path.dirname(__file__) + os.path.sep + "globals.json"

    def __init__(self) -> None:

        if not os.path.exists(self._path):
            self._create_globals()

        with open(self._path, "r") as f:
            data = json.load(f)
        self.ignore = data["ignore"]
        self._API_KEY = data["API_KEY"]
        self._ORG_KEY = data["ORG_KEY"]
        self.models = data["models"]

    def __repr__(self) -> str:
        return f"Globals(ignore={self.ignore} API_KEY=HIDDEN, ORG_KEY=HIDDEN)"

    def _create_globals(self, path) -> None:

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

    def fetch_models(self):
        openai.api_key = self._API_KEY
        openai.org_key = self._ORG_KEY
        r_models = openai.Model.list()


    def api(self) -> str:
        return self._API_KEY

    def org(self) -> str:
        return self._ORG_KEY


globals = Globals()

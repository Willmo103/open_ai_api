import os.path
import fnmatch
import os
import json
import openai
import click

def populate_globals():

    # get the root install path to generate/look for globals.json
    path: str = os.path.dirname(__file__) + os.path.sep + "globals.json"

    # keys is a list of all the keys that need to be present in the json object
    keys: list = ["ignore", "requests", "API_KEY", "ORG_KEY"]
    defaults: dict = {"ignore": [], "requests": []}

    # read the object make sure all keys are present
    try:
        with open(path, "r") as f:
            data = json.load(f)
        assert all(key in data for key in keys)
        return
    except (FileNotFoundError, json.JSONDecodeError):
        print("No globals.json file found, generating globals.json...")
        data = defaults.copy()
        data["API_KEY"] = input("Enter your openai API key: 'sk-...'\n> ")
        data["ORG_KEY"] = input("Enter your openai ORG key: 'org-...'\n> ")

        with open(path, "w") as f:
            json.dump(data, f, indent=4)

        print("globals.json created:\n", json.dumps(data, indent=4))
        return


def remove_pwd(path):
    pwd = os.path.normpath(os.getcwd())
    if path.startswith(pwd):
        stripped_path = path[len(pwd) + 1 :]
        return stripped_path
    else:
        return path


def create_directory_structure(data, path):
    """Create directory structure based on JSON object"""
    if isinstance(data, dict):
        for key, value in data.items():
            new_path = os.path.join(path, str(key))
            if isinstance(value, str):
                with open(new_path, "w") as f:
                    f.write(value)
            else:
                os.makedirs(new_path, exist_ok=True)
                create_directory_structure(value, new_path)


@click.command()
@click.argument("prompt", type=click.Path(exists=True))
@click.argument("-s", "--size", default=)
def code_edit(prompt):

    # I was having trouble trying to pull the variables from the .env file,
    # so since I'm relying on the globals.json file i could just use it to
    # hold the api key.

    # verify globals.json exists
    populate_globals()

    # load env
    with open("globals.json", "r") as f:
        data = json.load(f)

    # Set the environment variables from .env file
    openai.api_key = data["API_KEY"]
    openai.organization = data["ORG_KEY"]

    # uncomment to get the list of models saved locally
    # if openai.api_key:
    #     data = openai.Model.list()
    #     with open("models.json", 'w') as f:
    #         json.dump(data, f, indent=4)
    #     return

    # Read the contents of the prompt file
    with open(prompt, "r") as f:
        prompt_text = f.read()
    # print(prompt_text)

    # Use the OpenAI API to generate code based on the prompt
    response = openai.Completion.create(
        engine="code-davinci-002", prompt=prompt_text, max_tokens=1024, temperature=0.2
    )

    # Get the generated code from the response
    generated_code = response.choices[0].text.strip()

    # Print and save the generated code
    # print(generated_code)
    with open("globals.json", "r") as f:
        data = json.load(f)

    data["requests"].append(response)
    # This will eventually send the request to a database for saving,
    # for now they will be logged in the globals.json, and a script will populate them into the
    # database once the connection is ready

    with open("globals.json", "w") as f:
        json.dump(data, f)

    # Save the generated code to a file
    basename = os.path.basename(prompt).split(".")
    if len(basename) > 1:
        ext = basename[1]
    else:
        ext = basename[0]

    new_filename = f'{prompt}_edited.{ext}'
    with open(new_filename, "w") as f:
        f.write(generated_code)

    if click.confirm("Would you like to overwrite the original file with the response?", default=False):
        with open(prompt, "w") as f:
            f.write(generated_code)

    return


@click.command()
@click.option("-a", "--add", is_flag=True, help="Add a file to the ignore list")
@click.option("-d", "--delete", is_flag=True, help="Delete a file from the ignore list")
@click.option(
    "-l", "--list", "list_", is_flag=True, help="List all files in the ignore list"
)
def code_edit_ignore(add, delete, list_):
    # Load the JSON file
    with open("globals.json", "r") as f:
        data = json.load(f)

    ignored_files = data["ignore"]

    if list_:

        # List all the files in the ignore list
        for i, item in enumerate(ignored_files):
            print(f"{i}: {item}")

    elif add:

        # Prompt the user to enter a filename to add
        filename = click.prompt("Enter a filename to ignore")
        if filename in ignored_files:
            click.echo(f"{filename} is already in the ignore list.")

        else:
            # Confirm with the user before adding the file to the ignore list
            if click.confirm(f"Add {filename} to the ignore list?"):
                ignored_files.append(filename)
                # Update the JSON file
                with open("globals.json", "w") as f:
                    json.dump(data, f, indent=4)

    elif delete:
        # Prompt the user to select a file to delete
        for i, item in enumerate(ignored_files):
            print(f"{i}: {item}")
        selection = click.prompt("Enter the number of the item to delete", type=int)

        if selection < 0 or selection >= len(ignored_files):
            click.echo(f"Invalid selection: {selection}")

        else:
            # Confirm with the user before deleting the file from the ignore list
            filename = ignored_files[selection]

            if click.confirm(f"Delete {filename} from the ignore list?"):
                ignored_files.pop(selection)
                # Update the JSON file

                with open("globals.json", "w") as f:
                    json.dump(data, f, indent=4)

    else:
        # No options specified, so just list all files in the ignore list
        for i, item in enumerate(ignored_files):
            print(f"{i}: {item}")


@click.command()
@click.option(
    "-a",
    "--all",
    is_flag=True,
    help="Creates full file structure adding empty dicts for all directories and empty str for all files",
)
@click.argument("dir_path", type=click.Path(exists=True))
def dir_to_json(dir_path, all):
    """"""
    # Get the directory name from the dir_path argument
    directory_name = os.path.basename(os.path.abspath(dir_path))

    # remove the pwd from the path to avoid extra nesting
    dir_path = remove_pwd(os.path.normpath(dir_path))

    # Use the directory name to construct the output file name
    output_file_name = directory_name + "_context.json"

    with open("globals.json", "r") as f:
        data = json.load(f)

    ignored_files: list = data["ignore"]

    # Create an empty dictionary to store the file tree
    file_tree = {}

    # Traverse the directory and get the file tree
    for root, dirs, files in os.walk(dir_path):
        # print(root, "\n\n")
        current_dir = file_tree
        # Traverse all the directories in the current directory
        for directory in os.path.normpath(root).split(os.path.sep):
            ignore_dir = False
            for pattern in ignored_files:
                if fnmatch.fnmatch(directory, pattern):
                    ignore_dir = True
            if ignore_dir:
                if all:
                    current_dir = current_dir.setdefault(
                        os.path.basename(os.path.abspath(directory)), {}
                    )
                break
            current_dir = current_dir.setdefault(
                os.path.basename(os.path.abspath(directory)), {}
            )
        else:
            # Traverse all the files in the current directory
            for filename in files:
                # Check if the file matches the ignored_files patterns
                ignore_file = False
                for pattern in ignored_files:
                    if fnmatch.fnmatch(filename, pattern):
                        ignore_file = True
                        break
                if ignore_file:
                    if all:
                        current_dir[filename] = ""
                    continue

                # Get the full path of the file
                filepath = os.path.join(root, filename)

                # Read the contents of the file
                with open(filepath, "r") as f:
                    try:
                        file_contents = f.read()
                    except UnicodeDecodeError as e:
                        print(
                            f"""Encountered an error:

`{e}`

while parsing `{filepath}`.
consider updating your ignore list by running
'codex_ignore --add' to add an ignored extension or directory.
"""
                        )
                        return
                # Add the file contents to the file tree
                current_dir[filename] = file_contents

    # Save the file tree as a JSON file with the constructed output file name
    with open(output_file_name, "w") as f:
        json.dump(file_tree, f)

    return


@click.command()
@click.argument("json_obj", type=click.Path(exists=True))
@click.argument("path", type=click.Path())
def generate_directory(json_obj, path):
    """Generate directory structure based on JSON object"""
    with open(json_obj) as f:
        data = json.load(f)
    create_directory_structure(data, path)
    click.echo(f"Directory structure generated at {path}")

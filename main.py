import os
import json
import openai
import click
from dotenv import load_dotenv



@click.command()
@click.argument('prompt', type=click.Path(exists=True))
def code_edit(prompt):
    # load env
    load_dotenv(".env")

    # Set the environment variables from .env file
    openai.api_key = os.getenv("OPENAI_API_KEY")
    openai.organization = os.getenv("OPENAI_ORG_KEY")

    # Read the contents of the prompt file
    with open(prompt, 'r') as f:
        prompt_text = f.read()

    # Use the OpenAI API to generate code based on the prompt
    response = openai.Completion.create(
        engine="davinci-codex",
        prompt=prompt_text,
        max_tokens=1024,
        temperature=0.5
    )

    # Get the generated code from the response
    generated_code = response.choices[0].text.strip()

    # Print and save the generated code
    # print(generated_code)
    with open("globals.json", "r") as f:
        data = json.load(f)

    data['requests'].append(response)

    with open("globals.json", 'w') as f:
        json.dump(data, f)

    # Save the generated code to a file
    with open(prompt, 'w') as f:
        f.write(generated_code)


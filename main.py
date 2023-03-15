import os
import json
import openai
import click

# Set the environment variables from .env file
openai.api_key = os.environ.get("OPENAI_API_KEY")
openai.organization = os.environ.get("OPENAI_ORG_KEY")

@click.command()
@click.argument('prompt', type=click.Path(exists=True))
def code_edit(prompt):
    # Read the contents of the prompt file
    with open(prompt, 'r') as f:
        prompt_text = f.read()

    # Use the OpenAI API to generate code based on the prompt
    response = openai.Completion.create(
        engine="davinci-codex",
        prompt=prompt_text,
        max_tokens=1024,
        n_top=1,
        temperature=0.5
    )

    # Get the generated code from the response
    generated_code = response.choices[0].text.strip()

    # Print and save the generated code
    print(generated_code)
    with open(prompt+"_copy.json", 'w') as f:
        json.dump(response, f)

    # Save the generated code to a file
    with open(prompt+"_copy", 'w') as f:
        f.write(generated_code)

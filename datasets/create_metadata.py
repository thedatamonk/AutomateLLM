"""
This script loops over all an offline dump of code examples of third party APIs of trigger.dev.

Original source: https://trigger.dev/apis

We then use GPT-4 to generate two line summary of each code snippet and then append it to a JSON object.
The JSON object is stored in `integration_metadata.json`.

As part of the code, we already have run this script and provided the output JSON file.
If you want to overwrite this file, run this script in your CLI.

python create_metadata.py

"""
import os
import json
from openai import OpenAI

# Assuming 'integrations' is your base directory
base_dir = 'integrations'

llm_client = OpenAI()

def code2text(example_file_path):

    with open(example_file_path, 'r', encoding='utf-8') as file:
        code_snippet = file.read()

        code2text_prompt = f"""
Here is a code snippet. Your job is to understand the code and generate 1-2 line description in English about -
    - what task the code is trying to do
    - how it's trying to do the task?

Code snippet:

{code_snippet}

Description:

"""
        completion = llm_client.chat.completions.create(
                                    model="gpt-4-0125-preview",
                                    temperature=0.0,
                                    messages=[
                                        {"role": "system", "content": "You are an expert software engineer who can understand complex code in any programming language and translate it to layman English."},
                                        {"role": "user", "content": code2text_prompt}
                                    ]
                                )
        
        print (f"Code explanantion: {completion.choices[0].message.content}\n\n")

        return completion.choices[0].message.content


if __name__ == "__main__":

    # Initialize the JSON structure
    integrations_json = {"integrations": []}

    # Iterate over each API directory within 'integrations'
    for api_name in os.listdir(base_dir):
        api_path = os.path.join(base_dir, api_name)
        
        if os.path.isdir(api_path):

            # Prepare the dictionary for this API
            api_dict = {"api_name": api_name, "examples": []}

            # Iterate over each example file within the API directory
            for example_file in os.listdir(api_path):

                
                if example_file.endswith(".txt"):
                    # Add the example file to the API's list of examples
                    print (f"Processing {example_file}...")
    
                    example_path = os.path.join(api_path, example_file)

                    example_dict = {
                        "name": example_file,
                        "description": code2text(example_file_path=example_path)
                    }
                    api_dict["examples"].append(example_dict)

            # Add the API dictionary to the main JSON structure
            integrations_json["integrations"].append(api_dict)

    # Convert the Python dictionary to a JSON string for display or use
    # json_output = json.dumps(integrations_json, indent=4)


    with open("./datasets/integration_metadata.json", "w") as outfile:
        json.dump(integrations_json, outfile, indent=4)
    
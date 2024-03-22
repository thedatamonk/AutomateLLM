from typing import List, Dict
from openai import OpenAI
import os
import re
import json
import schemas
from utils.rag_utils import is_valid_json, load_examples
from collections import defaultdict
from dotenv import load_dotenv
from prompt_templates import TASKS_BREAKDOWN_PROMPT

load_dotenv()
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')

class AutomateRAG:
    def __init__(self, main_llm: str = "gpt-4-0125-preview", embed_llm: str = "text-embedding-ada-002") -> None:
        self.main_llm = main_llm
        self.main_llm_client = OpenAI()
        self.embed_llm = embed_llm
        self.valid_integrations = ['sendgrid', 'airtable', 'gmail', 'linear', 'slack', 'supabase', 'github', 'openai', 'caldotcom']
        
        with open("./datasets/integration_metadata.json", 'r') as infile:
            self.integrations_metadata = json.load(infile)
            print ("Integrations metadata loaded successfully.")
        

    def automate(self, job_description: str):
        """
        Given a job description, break down into tasks and then generate equivalent `trigger.dev` TypeScript code
        which when executed will create the job.
        
        Steps to follow - 

            1. Break down the job description into 1 or more tasks. Each step should be such that it can be implemented using `trigger.dev` SDK and its integrations.
            
            2. Identify the job trigger and its type. This can be an event, webhook or scheduled trigger. 
            
            3. Identify the integrations that might be helpful. For instance, to send a email everyday at 4 PM, we will need tools like SendGrid, Gmail etc.
                Ensure the identified integrations are valid integrations of `trigger.dev`.
            
            4. Based on points 3, load all examples for the identified integrations.

            5. Add outputs of step 1, 2, 3 and 4 in a prompt and then generate the final automation code.
        """

        print (f"Job description\n{'--'*50}\n{job_description}\n")

        # Step 1 and 2: Break down the job into tasks and identify the job trigger
        tasks_and_trigger = self.break_job_into_tasks(job_description=job_description)

        prettified_json_output = json.dumps(tasks_and_trigger, indent=4)

        print (f"\nTasks and Trigger:\n{'--'*50}\n{prettified_json_output}\n")

        # Step 3: 
        # Identify unique integrations/third party APIs that are required to complete the job
        if is_valid_json(json_data=tasks_and_trigger, schema=schemas.TASKS_SCHEMA):
            usable_integrations = self.__parse_integrations(json_data=tasks_and_trigger)
            print (f"\nIdentified unique integrations:\n{'--'*50}\n{usable_integrations}\n")
        else:
            print ("\nLLM output does not conform to the tasks schema\n")
            usable_integrations = None      

        # Step 4: 
        # Based on the identified integrations in step 3, fetch all code examples for each identied integration
        # from trigger.dev documentation
        # The code examples can be found here: https://trigger.dev/apis
        # In the current implementation, we have copied the code examples manually and stored them in .txt files
        # See 'integrations/' directory in the project folder
        
        examples = self.fetch_all_integration_examples(integrations=usable_integrations)
        total_examples = sum([len(api_examples) for api, api_examples in examples.items()])

        print (f"{total_examples} integration examples loaded.\n\n")

        # Step 5: Generate final code using identified tasks, job trigger and the examples.
        automation_code = self.generate_code(
                                        job_description=job_description,
                                        tasks_and_trigger=tasks_and_trigger,
                                        usable_integrations=usable_integrations,
                                        examples=examples
                            )
        
        return automation_code

    def smart_automate(self, job_description: str):
        """
        Given a job description, break down into tasks and then generate equivalent `trigger.dev` TypeScript code
        which when executed will create the job.
        
        Steps to follow - 

            1. Break down the job description into 1 or more tasks. Each step should be such that it can be implemented using `trigger.dev` SDK and its integrations.
            
            2. Identify the job trigger and its type. This can be an event, webhook or scheduled trigger. 
            
            3. Identify the integrations that might be helpful. For instance, to send a email everyday at 4 PM, we will need tools like SendGrid, Gmail etc.
                Ensure the identified integrations are valid integrations of `trigger.dev`.
            
            4. Based on points 1, 2 and 3, load ONLY 'relevant' examples for each integration.

            5. Add outputs of step 1, 2, 3 and 4 in a prompt and then generate the final automation code.
        """

        print (f"Job description\n{'--'*50}\n{job_description}\n")
        
        # Step 1 and 2: Break down the job into tasks and identify the job trigger
        tasks_and_trigger = self.break_job_into_tasks(job_description=job_description)

        prettified_json_output = json.dumps(tasks_and_trigger, indent=4)

        print (f"\nTasks and Trigger:\n{'--'*50}\n{prettified_json_output}\n")

        # Step 3:
        # Identify unique integrations/third party APIs that are required to complete the job
        if is_valid_json(json_data=tasks_and_trigger, schema=schemas.TASKS_SCHEMA):
            usable_integrations = self.__parse_integrations(json_data=tasks_and_trigger)
            print (f"\nUnique integrations:\n{'--'*50}\n{usable_integrations}\n")
        else:
            print ("\nLLM output does not conform to the tasks schema")
            usable_integrations = None

        # Step 4:
        # Based on the outputs of points 1, 2, and 3, fetch only relevant examples
        # from trigger.dev documentation. The 'relevancy' is defined as "How helpful are the examples in implementing the given tasks in hand."
        # The code examples can be found here: https://trigger.dev/apis
        # In the current implementation, we have copied the code examples manually and stored them in .txt files
        # See 'integrations/' directory in the project folder
        
        examples = self.fetch_select_integrations_examples(
                                            tasks_and_trigger=tasks_and_trigger,
                                            integrations=usable_integrations
                                        )
        
        total_examples = sum([len(api_examples) for api, api_examples in examples.items()])
        print (f"Identified and loaded {total_examples} integration examples.\n\n")

        # Step 5: Generate final code using identified tasks, job trigger and the examples.
        automation_code = self.generate_code(
                                            job_description=job_description,
                                            tasks_and_trigger=tasks_and_trigger,
                                            usable_integrations=usable_integrations,
                                            examples=examples
                            )
        
        return automation_code

    def generate_code(self, job_description, tasks_and_trigger, usable_integrations, examples):

        examples_string = "Here are the examples:\n"  
        
        for integration, examples in examples.items():
            examples_string += f"\n\nThird party API name: {integration}"
            examples_string += f"\n\nExamples of {integration}"

            for name, code in examples.items():
                examples_string += f"\n\nExample: {name}"
                examples_string += f"\n\nCode:\n\n{code}"
                
            examples_string += ("\n\n" + "**"*20)

        AUTOMATION_CODE_PROMPT_TEMPLATE = f"""
**Goal**

You are given the following inputs:
1. Job description: A job is defined as a sequence of tasks and it can be triggered due to an event, webhook or a schedule.
2. Sequence of tasks and job trigger as a JSON string
3. A list of third party APIs that you will need to accomplish your goal.
4. Examples showcasing different use cases of the third party APIs.

Your goal is to generate an equivalent [trigger.dev](https://trigger.dev/docs/documentation/introduction) Typescript code. Use the examples intelligently
to generate the code.

List of the third party APIs you can use: {usable_integrations}

"""

        prompt = AUTOMATION_CODE_PROMPT_TEMPLATE + "\n\n" + examples_string

        prompt += f"\n\n**Job description**: {job_description}"

        prompt += "\n\n**JSON string representing the job trigger details and the sequence of tasks**\n\n"

        tasks_and_trigger_string = json.dumps(tasks_and_trigger, indent=4)

        prompt += tasks_and_trigger_string

        prompt += """

**Output guidelines**

1. Only generate the typescript code as output. Do not include any backticks, quotes, explanatory text as part of the output.
2. The generated code should be valid Typescript code.
3. Add inline comments in the generated code to make it easy to understand.
"""
        prompt += "\n\nGenerated `trigger.dev` Typescript code:\n\n"
        
        code_output = self.__invoke_llm_api(llm_name=self.main_llm, query=prompt)

        return code_output

    def break_job_into_tasks(self, job_description: str) -> List[str]:
        """
        Given a job description, break down into one or more tasks
        """
        
        prompt = TASKS_BREAKDOWN_PROMPT + f"\n**Job Description**\n{job_description}"
        
        prompt += "\n\n**Predefined list of 3rd party APIs/integrations**\n" + f"{self.valid_integrations}"
        
        prompt += "\n\nOutput:\n"

        output = self.__invoke_llm_api(llm_name=self.main_llm, query=prompt)

        tasks_and_trigger = self.__parse_tasks_and_trigger(input_text=output)

        return tasks_and_trigger


    def __parse_tasks_and_trigger(self, input_text):

        try:
            json_data = json.loads(input_text)
            return json_data
        except json.JSONDecodeError as e:
            print (f"LLM output is not a valid JSON.\n\nThe output:\n\n{input_text}")
            print (f"\n\nTrying out some strategies to convert the output into a valid JSON....")
            cleaned_input_text = input_text.lstrip("```json").rstrip("```")
            json_data = json.loads(cleaned_input_text)
            return json_data
        
    
    def __parse_integrations(self, json_data):
        """
        Extracts unique integration values from both the job_trigger and tasks sections
        of a JSON object conforming to the specified schema.

        :param json_data: The JSON object conforming to the schema.
        :return: A set of unique integration values.
        """
        # Initialize a set to hold unique integration values
        unique_integrations = set()

        # Extract integrations from the job_trigger section
        if 'job_trigger' in json_data and 'integrations' in json_data['job_trigger']:
            unique_integrations.update(json_data['job_trigger']['integrations'])

        # Extract integrations from each task in the tasks section
        if 'tasks' in json_data:
            for task in json_data['tasks']:
                if 'integrations' in task:
                    unique_integrations.update(task['integrations'])

        return list(unique_integrations)

    def fetch_all_integration_examples(self, integrations):
        """
        Given a list of integrations, load all the examples for each integration
        """
        all_examples = {}

        for integration in integrations:
            if integration in self.valid_integrations:
                all_examples[integration] = load_examples(dataset_path=f"integrations/{integration}")
        
        return all_examples
    

    def fetch_select_integrations_examples(self, tasks_and_trigger, integrations):
        """
        Given a list of integrations and a JSON object representing the task breakdown of a job,
        use LLM to identify 'relevant' examples that will help generate automation code
        for the given job.
        """
        # Group tasks by integration and create a dictionary
        # where keys are the integration/third party API names
        # and values are the list of tasks that these APIs are relevant for
        integrations_to_tasks_mapping = defaultdict(list)
        for task in tasks_and_trigger['tasks']:
            if len(task['integrations']):
                for integration in task['integrations']:
                    integrations_to_tasks_mapping[integration].append(task['task_desc'])
        
        job_trigger = tasks_and_trigger['job_trigger']
        if len(job_trigger['integrations']):
            for integration in job_trigger['integrations']:
                integrations_to_tasks_mapping[integration].append(job_trigger['explanation'])
        
        assert set(integrations_to_tasks_mapping.keys()) == set(integrations), "Mismatch in the integrations."

        all_examples = {}

        # Use LLM to identify relevant code examples from a given list of code examples
        for integration, tasks in integrations_to_tasks_mapping.items():
            all_examples[integration] = self.identify_relevant_examples(integration, tasks, max_examples=2)
        
        # Load selected examples from their respective files
        selected_code_snippets = self.load_relevant_examples(all_examples)

        return selected_code_snippets
    
    def load_relevant_examples(self, input_dict):
        output_dict = defaultdict(list)

        for integration, examples_list in input_dict.items():
            if integration in self.valid_integrations:
                output_dict[integration] = load_examples(dataset_path=f"integrations/{integration}", select_examples=examples_list)

        return output_dict
    
    def identify_relevant_examples(self, integration, tasks, max_examples=1):

        print (f"Finding relevant examples for API: {integration}...")
        for item in self.integrations_metadata['integrations']:
            if item['api_name'] == integration:
                all_examples = item['examples']
                break
        

        prompt = f"""
You are given some example usecases for a third party API called {integration}.

Here is a JSON containing the examples:

{all_examples}

You are also given a list of tasks:

{tasks}

In order to accomplish your goal -

1. understand the tasks and their intent
2. understand the example JSON, in particular the `description` field of each example.
3. based on 1. and 2. figure out which examples can help accomplish the tasks.
4. fetch atleast 1 and atmost {max_examples} example usecases for each task.

Output format:
1. <EXAMPLE 1 NAME>: <Task for which this example will be helpful>
2. <EXAMPLE 2 NAME>: <Task for which this example will be helpful>
.
.


Output

"""

        output = self.__invoke_llm_api(llm_name=self.main_llm, query=prompt)

        pattern = r"\b[\w-]+\.txt\b"
        selected_examples = re.findall(pattern, output)

        print (f"Here are the selected examples for API {integration}:\n\n{selected_examples}\n\n")

        return selected_examples[:max_examples]
    
    def __invoke_llm_api(self, llm_name, query, llm_provider='openai'):
        """
        Generic method to call LLM API
        """

        if llm_provider == "openai":
            completion = self.main_llm_client.chat.completions.create(
                            model=llm_name,
                            temperature=0.0,
                            messages=[
                                {"role": "system", "content": "You are an expert software engineer who is proficient in TypeScript."},
                                {"role": "user", "content": query}
                            ]
                        )
            return completion.choices[0].message.content
        else:
            raise ValueError(f"{llm_provider} LLM provider currently not supported. Please use OpenAI.")


from typing import List, Dict
from openai import OpenAI
import os
import re
import json
import schemas
from utils.rag_utils import is_valid_json, load_examples, load_example
from collections import defaultdict

os.environ['OPENAI_API_KEY'] = "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"

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
            
            4. Based on points 1 and 3, fetch relevant examples.

            5. Based on points 1, 2 and 3, fetch relevant sections of documentation so that only valid methods and attributes are used.

            6. Add outputs of points 4 and 5 as context, and generate the final code iteratively.

            7. Code correction
        """

        print (f"Job description\n{'--'*50}\n{job_description}\n")

        # break down the job into tasks and identify the job trigger
        tasks_and_trigger = self.break_job_into_tasks(job_description=job_description)

        prettified_json_output = json.dumps(tasks_and_trigger, indent=4)

        print (f"Tasks and Trigger:\n{'--'*50}\n{prettified_json_output}\n")

        # identify unique integrations/third party APIs that are required to complete the job
        # these APIs also help fetch relevant code examples from trigger.dev documentation (link: https://trigger.dev/apis)
        if is_valid_json(json_data=tasks_and_trigger, schema=schemas.TASKS_SCHEMA):
            usable_integrations = self.__parse_integrations(json_data=tasks_and_trigger)
            print (f"Unique integrations:\n{'--'*50}\n{usable_integrations}\n")
        else:
            print ("LLM output does not conform to the tasks schema")
            usable_integrations = None      

        # based on the identified integrations, fetch relevant code examples from trigger.dev documentation
        # in the current implementation, we have copied the code examples manually and stored them in .txt files
        # See integrations/ directory in the project folder
        examples = self.fetch_examples_for_integrations(integrations=usable_integrations)

        print (f"Examples:\n{examples}")

        # Generate final code using identified tasks, job trigger and the examples.
        automation_code = self.generate_code(
                                        job_description=job_description,
                                        tasks_and_trigger=tasks_and_trigger,
                                        usable_integrations=usable_integrations,
                                        examples=examples
                            )
        
        return automation_code

    def pro_automate(self, job_description: str):
        
        print (f"Job description\n{'--'*50}\n{job_description}\n")
        
        # break down the job into tasks and identify the job trigger
        tasks_and_trigger = self.break_job_into_tasks(job_description=job_description)

        prettified_json_output = json.dumps(tasks_and_trigger, indent=4)

        print (f"Tasks and Trigger:\n{'--'*50}\n{prettified_json_output}\n")

        # identify unique integrations/third party APIs that are required to complete the job
        # these APIs also help fetch relevant code examples from trigger.dev documentation (link: https://trigger.dev/apis)
        if is_valid_json(json_data=tasks_and_trigger, schema=schemas.TASKS_SCHEMA):
            usable_integrations = self.__parse_integrations(json_data=tasks_and_trigger)
            print (f"Unique integrations:\n{'--'*50}\n{usable_integrations}\n")
        else:
            print ("LLM output does not conform to the tasks schema")
            usable_integrations = None


        examples = self.smart_fetch_integrations_examples(
                                            tasks_and_trigger=tasks_and_trigger,
                                            integrations=usable_integrations
                                        )
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

        print (f"Prompt: {prompt}")
        print ("-----*------*--------")
        code_output = self.__invoke_llm_api(llm_name=self.main_llm, query=prompt)

        return code_output

    def break_job_into_tasks(self, job_description: str) -> List[str]:
        """
        Given a job description, break down into one or more tasks
        """
        TASKS_BREAKDOWN_PROMPT = """
        **Goal**
        You are given a job description. A Job is defined as a sequence of tasks and it can be triggered due to an event, webhook or a schedule

        Your goal is to understand the job and - (1) Identify the job trigger (2) Break down the job into a sequence of tasks.

        Strictly adhere to the output format. The output format must be a valid JSON and its schema is defined below under the **Output format** section.

        Do not include any leading or trailing backticks, single quotes, double quotes or any other symbols in the output.

        The output should always start with a { and end with a }

        **Output format**
        
        {
            "job_trigger": {
                "type": <<trigger_type>>, // valid values are 'webhook', 'event', 'schedule'
                "explanation": <<One line explanation for why this trigger type is chosen>>,
                "params": <<Relevant trigger params>> // For example, for a 'schedule' trigger, it can be the actual schedule like 'Every Friday at 4 PM'.
                "integrations: <<List of third party APIs required to implement the job trigger>> // NOTE: The third party APIs have to be selected from a predefined list of APIs. Also, in case no API is required or no valid option is found in the predefined list, keep the list empty.
            },

            "tasks": [
                {   
                    "task_sequence_id": 1,
                    "task_desc": <<Exactly one line concise and accurate description of the task>>,
                    "integrations: <<List of third party APIs required to implement the task>> // NOTE: The third party APIs have to be selected from a predefined list of APIs. Also, in case no API is required or no valid option is found in the predefined list, keep the list empty.

                },
                {
                    "task_sequence_id": 2,
                    "task_desc": <<Exactly one line concise and accurate description of the task>>,
                    "integrations: <<List of third party APIs required to implement the task>> // NOTE: The third party APIs have to be selected from a predefined list of APIs. Also, in case no API is required or no valid option is found in the predefined list, keep the list empty.

                },
                .
                .
                .
                {
                    "task_sequence_id": N,
                    "task_desc": <<Exactly one line concise and accurate description of the task>>,
                    "integrations: <<List of third party APIs required to implement the task>> // NOTE: The third party APIs have to be selected from a predefined list of APIs. Also, in case no API is required or no valid option is found in the predefined list, keep the list empty.

                }
            ]
        }

        **Examples**

        Example 1:
        Job Description: Update Airtable when a new subscription is added to Stripe.

        Output:

        {
            "job_trigger": {
                "type": "webhook",
                "explanation": "Trigger type is 'webhook' because job will listen to 'New subscription' events from Stripe API",
                "params": "New subscription is added to Stripe database",
                "integrations": ["stripe"]
            },

            "tasks": [
                {   
                    "task_sequence_id": 1,
                    "task_desc": "Add a new record containing the new subscription details in Airtable.",
                    "integrations": ["airtable"]
                }
            ]
        }        
        
        Example 2:
        Job Description: Send an activity summary email, and post it to Slack at 4PM every Friday.

        Output:

        {
            "job_trigger": {
                "type": "schedule",
                "explanation": "Trigger type is 'schedule' because job will trigger every Friday at 4 PM.",
                "params": "Every Friday at 4 PM.",
                "integrations": []
            },

            "tasks": [
                {   
                    "task_sequence_id": 1,
                    "task_desc": "Send a weekly summary email to users who have opted-in to receive weekly summaries.",
                    "integrations": ["sendgrid"]
                },
                {
                    "task_sequence_id": 2,
                    "task_desc": "Send a slack message to relevant channel informing that a weekly summary has been sent to the relevant users.",
                    "integrations": ["slack"]
                }
            ]
        }

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
        

    def identify_integrations(self, job_trigger: Dict, tasks: str) -> List[str]:
        """
        Given a job trigger and the identified tasks, identify what integrations we might need to implement the tasks.
        """
        INTEGRATION_PROMPT_TEMPLATE = f"""
        
        **Goal**
        You are given the following details of a job that needs to be automated using [trigger.dev](https://trigger.dev/docs/documentation/introduction) code.

        1. Job trigger details: Type of trigger and the relevant parameters
        2. List of tasks that need to be performed in the given sequence to complete the job.

        Your goal is to identify the 3rd party APIs that might be required to implement these tasks.
        Note that the identified APIs need to be from a predefined list of APIs/integrations that `trigger.dev` supports.
        This predefined list is also provided to you as input.

        **Guidelines to follow**

        1. Do not hallucinate 3rd party APIs. Strictly select 1 or more options from the predefined list.
        2. Strictly adhere to the output format.
        3. For a task, if more than one API alternatives are present, then select only one. For instance, if the task is to send an email, trigger.dev has integrations with both Gmail and SendGrid, then you have to select only one of these.

        {job_trigger}

        **Job Tasks**
        {tasks}

        **List of predefined API/integrations**
        {self.valid_integrations}

        **Output format**

        A numbered list where each list item contains the API Name and one line describing the purpose of that API.
        The API name and the one-line description should be separate by a ': ' (without the quotes).
        
        1. <<API_NAME_1>>: <<DESCRIPTION_1>>
        2. <<API_NAME_2>>: <<DESCRIPTION_2>>
        .
        .
        N. <<API_NAME_N>>: <<DESCRIPTION_N>>

        """

        integrations_output = self.__invoke_llm_api(llm_name=self.main_llm, query=INTEGRATION_PROMPT_TEMPLATE)

        integrations = self.__parse_integrations(integrations_output)

        return integrations, integrations_output
    
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

    def fetch_examples_for_integrations(self, integrations):

        all_examples = {}

        for integration in integrations:
            if integration in self.valid_integrations:
                all_examples[integration] = load_examples(dataset_path=f"integrations/{integration}")
        
        return all_examples
    

    def smart_fetch_integrations_examples(self, tasks_and_trigger, integrations):
        """
        Out of all the examples for a given API, retrieve only those examples that can really help
        implementing the job trigger and the individual tasks.

        So I think in order to implement this, we will need to identify what the example is doing and generate a nice summary
        of each code example.

        For each tasks and its integration, first filter out examples for that integration only
        Then filter out examples, where the integration is trying to do something similar to what
        is asked in the given task

        If more than 1 examples are relevant, then fetch only first k.
        """
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

        for integration, tasks in integrations_to_tasks_mapping.items():
            all_examples[integration] = self.select_top_k_examples(integration, tasks)
        
        selected_code_snippets = self.fetch_selected_examples(all_examples)

        return selected_code_snippets
    
    def fetch_selected_examples(self, input_dict):
        output_dict = defaultdict(list)

        for integration, examples_list in input_dict.items():
            if integration in self.valid_integrations:
                output_dict[integration] = load_examples(dataset_path=f"integrations/{integration}", select_examples=examples_list)

        return output_dict
    
    def select_top_k_examples(self, integration, tasks):

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
4. fetch at least 2 example usecases for each task.

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

        return selected_examples
    
    def __invoke_llm_api(self, llm_name, query, llm_provider='openai'):

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


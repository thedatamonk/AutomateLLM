from typing import List, Dict
from openai import OpenAI
import os
import re

os.environ['OPENAI_API_KEY'] = "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"

class AutomateRAG:
    def __init__(self, main_llm: str = "gpt-4-0125-preview", embed_llm: str = "text-embedding-ada-002") -> None:
        self.main_llm = main_llm
        self.main_llm_client = OpenAI()
        self.embed_llm = embed_llm
        self.valid_integrations = ['sendgrid', 'airtable', 'gmail', 'linear', 'slack', 'supabase', 'github', 'openai'] # TODO: Maintain a list of integrations along with their descriptions


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

        print (f"Job description\n{'--'*50}\n{job_description}")
        job_trigger, tasks = self.break_job_into_tasks(job_description=job_description)

        print (f"Job Trigger\n{'--'*50}\n{job_trigger}")
        print (f"Tasks\n{'--'*50}\n{tasks}")
        
        integrations, integrations_output = self.identify_integrations(job_trigger=job_trigger, tasks=tasks)

        integrations = list(set(integrations))
        print (f"Here is the list of integrations:\n{integrations}")
        print (f"Here is the LLM output for integrations:\n{integrations_output}")

    def break_job_into_tasks(self, job_description: str) -> List[str]:
        """
        Given a job description, break down into one or more tasks
        """
        TASKS_BREAKDOWN_PROMPT = f"""
        **Goal**
        You are given a job description. A Job is defined as a sequence of tasks and it can be triggered due to an event, webhook or a schedule

        Your goal is to understand the job and break it down into a sequence of tasks.

        **Guidelines to follow**
        
        1. The first task should always be a trigger.
        2. The subsequent tasks should be ordered.
        3. Strictly adhere to the output format

        **Examples**

        Example 1:
        Job Description: Update Airtable when a new subscription is added to Stripe.

        Tasks:
        
        Job trigger:
            - webhook
            - Trigger type is 'webhook' because job will listen to 'New subscription' events from Stripe API
            - New subscription is added to Stripe database
        
        1. Add a new record containing the new subscription details in Airtable.

        Example 2:
        Job Description: Send an activity summary email, and post it to Slack at 4PM every Friday.

        Tasks:

        Job trigger:
            - schedule
            - Trigger type is 'schedule' because job will trigger every Friday at 4 PM.
            - Every Friday at 4 PM.
        
        1. Send a weekly summary email to users who have opted-in to receive weekly summaries.
        2. Send a slack message to relevant channel informing that a weekly summary has been sent to the relevant users.

        **Job Description**
        {job_description}
        
        **Output format**
        
        Tasks:

        Job trigger: 
            - <<trigger_type>> // valid values are 'webhook', 'event', 'schedule'
            - <<One line explanation for why this trigger type is chosen>>
            - Relevant trigger params // For example, for a 'schedule' trigger, it can be the actual schedule like 'Every Friday at 4 PM'.
        1. Task 1
        2. Task 2
            .
            .
            .
        N. Task N

        """
        
        tasks_breakdown_output = self.__invoke_llm_api(llm_name=self.main_llm, query=TASKS_BREAKDOWN_PROMPT)

        job_trigger, tasks = self.__parse_tasks_and_trigger(input_text=tasks_breakdown_output)

        return job_trigger, tasks



    def __parse_tasks_and_trigger(self, input_text):
        # Find the start of the Job trigger section
        trigger_start_index = input_text.find("Job trigger:")

        # Assuming the tasks always start with "1.", find the start of the tasks
        tasks_start_index = input_text.find("1.")
        
        # Extract the Job trigger section
        job_trigger_section = input_text[trigger_start_index:tasks_start_index].strip()
        
        # Extract the tasks section
        tasks_section = input_text[tasks_start_index:].strip()
        
        return job_trigger_section, tasks_section

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
    
    def __parse_integrations(self, integration_str):
        # Regular expression to match any non-whitespace characters before a colon
        # \S+ matches one or more non-whitespace characters
        # (?=:) is a positive lookahead for a colon, ensuring we match words that are immediately followed by a colon
        pattern = re.compile(r'\S+(?=:)')
    
        # Find all matches of the pattern in the text
        matches = pattern.findall(integration_str)
        
        # Return the list of words found before colons
        return matches


    def fetch_examples(self, integrations: List[str]):
        """
        This is where we will do retrieval from qdrant vector DB
        We will fetch all examples for this integration
        """
        pass

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


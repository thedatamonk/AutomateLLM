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
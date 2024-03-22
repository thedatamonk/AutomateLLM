# AutomateLLM

`AutomateLLM` is an attempt to replicate the functionality of Zapier's "Create a Zap with AI" feature.

![Create a Zap with AI](assets/create-a-zap-with-ai.png)

With this, a user can automate workflows like - 
1. "Send an onboarding email when a new user signs up on my website"
2. "Send a slack reminder notification to all team members who haven't updated their JIRA tickets."

🤩🤩 ***And all this by simply using natural language!!*** 🤩🤩

## Scope

Fully replicating this feature involves multiple moving components and may require several months to implement it production grade version like that of Zapier.

In this project, we will focus on developing the RAG (Retrieval Augmented Generation) pipeline that will try to generate automation code as accurately as possible from a plain english sentence.

## Solution
- To solve this task, we will have to convert an english description of a worflow to its equivalent code. This generated code will be executed by some automation code library and the workflow will be created. For this project, we will use [trigger.dev](https://trigger.dev/).

- We will use GPT-4 (`gpt-4-0125-preview`) as our main LLM to generate the code. But this can we swapped with any other LLM.

- To guide our LLM in this task, we will use a mix of prompt engineering as well as retrieve relevant code examples from the [official documentation of Trigger.dev](https://trigger.dev/apis).

**RAG #1: Retrieve all examples**

![RAG 1 pipeline](assets/RAG_1_AutomateLLM.png)

**RAG #2: Retrieve only relevant examples**

![RAG 2 pipeline](assets/RAG_2_AutomateLLM.png)



## Files and folders
## Next steps

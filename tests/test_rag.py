"""
Thi script is use to test the RAG pipelines with sample inputs.
"""
from rag import AutomateRAG

def test_automate():
    rag = AutomateRAG()

    # output = rag.automate("Post Linear issues to Slack every weekday at 9am using Cron.")
    # output = rag.pro_automate("Post Linear issues to Slack every weekday at 9am using Cron.")
    # print (f"Code output:\n{output}")

    # output = rag.automate("Send an email via Gmail to the user confirming that 'Account deletion was successful' when a user deletes their Slack account. All slack user accounts are stored in airtable database. So you will have to delete the appropriate user records from airtable.")
    output = rag.pro_automate("Send an email via Gmail to the user confirming that 'Account deletion was successful' when a user deletes their Slack account. All slack user accounts are stored in airtable database. So you will have to delete the appropriate user records from airtable.")
    print (f"Code output:\n{output}")

    # output = rag.automate("Every Monday at 1AM, send an email summarizing the Github commits that are created over the last week. For email, please use Sendgrid. Use OpenAI GPT3.5 to summarize the commits.")
    # output = rag.pro_automate("Every Monday at 1AM, send an email summarizing the Github commits that are created over the last week. For email, please use Sendgrid. Use OpenAI GPT3.5 to summarize the commits.")
    # print (f"Code output:\n{output}")
    
    # output = rag.automate("Whenever an SQL query returns a blank result or it's incorrect, send an email via Gmail to the user who ran the query. In the email mention why the query failed or returned empty results. Also specify which parameters from the user are required to correct the query. Now wait for the user's reply. Whenever the user replies to the email, trigger a webhook to call a Python script that parses the email response data and reruns the SQL query again. For running the SQL query, you can assume that the user is using Airtable.")
    # print (f"Code output:\n{output}")

if __name__ == "__main__":
    test_automate()
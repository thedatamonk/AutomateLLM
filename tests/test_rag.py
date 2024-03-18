from rag import AutomateRAG

def test_break_job_into_tasks():
    rag = AutomateRAG()

    # rag.automate("Post Linear issues to Slack every weekday at 9am using Cron.")

    # rag.automate("Send a Supabase onboarding email when a user confirms their Supabase email address. Use SendGrid to send the email.")

    # rag.automate("Everyday at 5PM, send an email summarizing the Github commits that are created on that day. For email, please use Gmail. Use OpenAI GPT4 to summarize the commits.")

    rag.automate("Whenever an SQL query returns a blank result or it's incorrect, send an email via Gmail to the user who ran the query. In the email mention why the query failed or returned empty results. Also specify which parameters from the user are required to correct the query. Now wait for the user's reply. Whenever the user replies to the email, trigger a webhook to call a Python script that parses the email response data and reruns the SQL query again. For running the SQL query, you can assume that the user is using Airtable.")

if __name__ == "__main__":
    test_break_job_into_tasks()
from rag import AutomateRAG

def test_break_job_into_tasks():
    rag = AutomateRAG()

    rag.automate("Post Linear issues to Slack every weekday at 9am using Cron.")

    # rag.automate("Send a Supabase onboarding email when a user confirms their Supabase email address. Use SendGrid to send the email.")

    # rag.automate("Everyday at 5PM, send an email summarizing the Github commits that are created on that day. Use OpenAI GPT4 to summarize the commits.")

    # rag.automate("Whenever an SQL query returns a blank result, send an email via Gmail based on certain parameters. Whenever the user replies to the email, trigger a webhook to parse and insert gmail response data into the SQL table again.")

if __name__ == "__main__":
    test_break_job_into_tasks()
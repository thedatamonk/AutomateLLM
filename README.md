# AutomateLLM


**User flow**
1. Job description in english
2. Break down jobn into tasks
    - 2.1. Identify job trigger - (webhook/event/schedule)
    - 2.2. Identify the sequence of tasks
3. For the job trigger and each task, identify if any third party APIs are required or not. If yes, then infer their names
4. Given the job trigger, tasks and the third party APIs, generate an equivalent `trigger.dev` code.

```ts
import { TriggerClient, eventTrigger } from "@trigger.dev/sdk";
import { google } from "googleapis";
import { JWT } from "google-auth-library";
import { Airtable } from "@trigger.dev/airtable";

// Initialize JWT for Gmail API
const auth = new JWT({
  email: process.env.GOOGLE_CLIENT_EMAIL,
  key: process.env.GOOGLE_PRIVATE_KEY!.split(String.raw`\n`).join("\n"),
  scopes: ["https://www.googleapis.com/auth/gmail.send"],
});
auth.subject = process.env.GOOGLE_IMPERSONATION_EMAIL;

// Initialize the Gmail API
const gmail = google.gmail({ version: "v1", auth });

// Initialize Airtable
const airtable = new Airtable({
  id: "airtable",
  token: process.env.AIRTABLE_TOKEN!,
});

// Define the job
client.defineJob({
  id: "sql-query-failure-notification",
  name: "Notify user on SQL query failure or empty result",
  version: "1.0.0",
  trigger: eventTrigger({
    name: "sql-query-failure",
    // Assuming there's a mechanism to trigger this event when an SQL query fails
    schema: {
      type: "object",
      properties: {
        userEmail: { type: "string" },
        queryDetails: { type: "string" },
        reason: { type: "string" },
      },
      required: ["userEmail", "queryDetails", "reason"],
    },
  }),
  run: async (payload, io, ctx) => {
    const { userEmail, queryDetails, reason } = payload;

    // Send an email to the user explaining the failure
    const emailBody = `Your SQL query failed due to: ${reason}. Query details: ${queryDetails}. Please reply to this email with corrected parameters.`;
    const email = `To: ${userEmail}\r\nSubject: SQL Query Failure Notification\r\n\r\n${emailBody}`;

    await io.runTask(
      "Send Gmail",
      async () => {
        await gmail.users.messages.send({
          userId: "me",
          requestBody: {
            raw: Buffer.from(email).toString("base64"),
          },
        });
      },
      { name: "Send Gmail", icon: "google" }
    );

    // Here you would wait for the user's reply and trigger a webhook to call a Python script
    // This part is not directly implementable in Trigger.dev as it requires external setup
    // to listen for the email reply and then trigger the webhook.

    // Assuming the webhook has been called and the Python script has parsed the email response
    // and provided the corrected SQL query parameters, we now rerun the SQL query in Airtable.

    // This is a placeholder for rerunning the SQL query in Airtable based on the parsed email response data.
    // The actual implementation would depend on the structure of your Airtable and the SQL query being used.
  },
});
```
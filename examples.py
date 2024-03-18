CODE_EXAMPLES = [
    {
        "job": "Send an activity summary email to users at 4 PM every Friday.",
        "automation_code": """
import { TriggerClient, cronTrigger } from "@trigger.dev/sdk";
import { SendGrid } from "@trigger.dev/sendgrid";
import { Slack } from "@trigger.dev/slack";
import { weeklySummaryDb } from "./mocks/db";
import { weeklySummaryEmail } from "./mocks/emails";

const sendgrid = new SendGrid({
  id: "sendgrid",
  apiKey: process.env.SENDGRID_API_KEY!,
});

const slack = new Slack({ id: "slack" });

// This Job sends a weekly summary email to users who have
// summariesEnabled = true, and then posts the total numbers to Slack.
client.defineJob({
  id: "weekly-user-activity-summary",
  name: "Weekly user activity summary",
  version: "1.0.0",
  integrations: { sendgrid, slack },
  trigger: cronTrigger({
    // Send every Friday at 4pm
    cron: "0 16 * * 5",
  }),
  run: async (payload, io, ctx) => {
    const users = await weeklySummaryDb.getUsers();

    let sentCount = 0;
    let notSentCount = 0;

    for (const user of users) {
      if (user.summariesEnabled) {
        await io.sendgrid.sendEmail(`Weekly summary for ${user.id}`, {
          to: user.email,
          // The 'from' email must be a verified domain in your SendGrid account.
          from: "hello@acme.inc",
          subject: "Your weekly summary",
          html: weeklySummaryEmail(user),
        });
        sentCount++;
      } else {
        notSentCount++;
      }
    }

    await io.slack.postMessage("Notify team", {
      text: `Weekly summary sent to ${sentCount} users and not sent to ${notSentCount} users`,
      // This has to be a channel ID, not a channel name
      channel: "YOUR_CHANNEL_ID",
    });
  },
});
""" 
    },
    {
        "job": "SendGrid send basic email.",
        "automation_code": """
import { TriggerClient, eventTrigger } from "@trigger.dev/sdk";
import { SendGrid } from "@trigger.dev/sendgrid";
import { z } from "zod";

export 
const sendgrid = new SendGrid({
  id: "sendgrid",
  apiKey: process.env.SENDGRID_API_KEY!,
});

// This job sends a basic email to a 'to' email address, a 'subject', a 'text' field and a 'from' email address.
client.defineJob({
  id: "sendgrid-send-basic-email",
  name: "SendGrid: send basic email",
  version: "1.0.0",
  trigger: eventTrigger({
    name: "send.email",
    schema: z.object({
      to: z.string(),
      subject: z.string(),
      text: z.string(),
      // The 'from' email address must be a verified domain in your SendGrid account.
      from: z.string(),
    }),
  }),
  integrations: {
    sendgrid,
  },
  run: async (payload, io, ctx) => {
    await io.sendgrid.sendEmail("send-email", {
      to: payload.to,
      from: payload.from,
      subject: payload.subject,
      text: payload.text,
    });
  },
});
"""
    },

    {
        "job": "Send an activity summary email, and post it to Slack at 4 PM every Friday.",
        "automation_code": """
import { TriggerClient, cronTrigger } from "@trigger.dev/sdk";
import { SendGrid } from "@trigger.dev/sendgrid";
import { Slack } from "@trigger.dev/slack";
import { weeklySummaryDb } from "./mocks/db";
import { weeklySummaryEmail } from "./mocks/emails";

const sendgrid = new SendGrid({
  id: "sendgrid",
  apiKey: process.env.SENDGRID_API_KEY!,
});

const slack = new Slack({ id: "slack" });

// This Job sends a weekly summary email to users who have
// summariesEnabled = true, and then posts the total numbers to Slack.
client.defineJob({
  id: "weekly-user-activity-summary",
  name: "Weekly user activity summary",
  version: "1.0.0",
  integrations: { sendgrid, slack },
  trigger: cronTrigger({
    // Send every Friday at 4pm
    cron: "0 16 * * 5",
  }),
  run: async (payload, io, ctx) => {
    const users = await weeklySummaryDb.getUsers();

    let sentCount = 0;
    let notSentCount = 0;

    for (const user of users) {
      if (user.summariesEnabled) {
        await io.sendgrid.sendEmail(`Weekly summary for ${user.id}`, {
          to: user.email,
          // The 'from' email must be a verified domain in your SendGrid account.
          from: "hello@acme.inc",
          subject: "Your weekly summary",
          html: weeklySummaryEmail(user),
        });
        sentCount++;
      } else {
        notSentCount++;
      }
    }

    await io.slack.postMessage("Notify team", {
      text: `Weekly summary sent to ${sentCount} users and not sent to ${notSentCount} users`,
      // This has to be a channel ID, not a channel name
      channel: "YOUR_CHANNEL_ID",
    });
  },
});
"""
    }

]
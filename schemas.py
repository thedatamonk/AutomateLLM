
TASKS_SCHEMA = {
  "type": "object",
  "properties": {
    "job_trigger": {
      "type": "object",
      "properties": {
        "type": {
          "type": "string",
          "enum": ["webhook", "event", "schedule"]
        },
        "explanation": {
          "type": "string"
        },
        "params": {
          "type": "string"
        },
        "integrations": {
          "type": "array",
          "items": {
            "type": "string"
          }
        }
      },
      "required": ["type", "explanation", "params", "integrations"],
      "additionalProperties": False
    },
    "tasks": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "task_sequence_id": {
            "type": "integer",
            "minimum": 1
          },
          "task_desc": {
            "type": "string"
          },
          "integrations": {
            "type": "array",
            "items": {
              "type": "string"
            }
          }
        },
        "required": ["task_sequence_id", "task_desc", "integrations"],
        "additionalProperties": False
      }
    }
  },
  "required": ["job_trigger", "tasks"],
  "additionalProperties": False
}

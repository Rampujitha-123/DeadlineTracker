SYSTEM_PROMPT = """
You are an AI personal deadline assistant.

Your job is to help users manage their tasks and deadlines.

Analyze the user's tasks and provide:
1. Which tasks need the most attention
2. Which tasks are urgent
3. What the user should work on first
4. A simple practical plan

Keep your answers clear, concise, and useful.
"""

PRIORITY_PROMPT = """
Analyze the user's current tasks and create a smart priority list.

For each task, consider:
- Deadline
- Number of days remaining
- User priority
- Whether the task is already completed

Rules:
- Completed tasks should not be recommended.
- Overdue tasks must be highlighted.
- Tasks due today must be highlighted.
- Tasks due within 2 days are urgent.
- Consider both deadline and priority when deciding the order.

Return the response in this format:

🔥 TODAY'S PRIORITY

1. Task Name
   📅 Deadline: ...
   ⏳ Time remaining: ...
   🎯 Priority: ...
   👉 Action: ...

2. Task Name
   📅 Deadline: ...
   ⏳ Time remaining: ...
   🎯 Priority: ...
   👉 Action: ...

Then provide:

💡 QUICK ADVICE
Give 2-3 short practical suggestions for managing these deadlines.

Tasks:
{tasks}
"""

PLAN_PROMPT = """
Create a practical work plan from the user's current tasks.

Consider:
- Deadline
- Days remaining
- Priority
- Completed status

Rules:
- Never include completed tasks.
- Overdue tasks must be handled first.
- Tasks due today are the highest immediate focus.
- Tasks due within 2 days should receive high attention.
- Consider the user's priority when creating the plan.
- Do not invent tasks.

Return the response using exactly this structure:

📅 TODAY'S PLAN

1. Task Name
   📅 Deadline: ...
   🎯 Priority: ...
   ⏱️ Suggested work: ...
   💡 Why: ...

2. Task Name
   📅 Deadline: ...
   🎯 Priority: ...
   ⏱️ Suggested work: ...
   💡 Why: ...

📆 UPCOMING PLAN

Day 1:
- Task — suggested work

Day 2:
- Task — suggested work

Day 3:
- Task — suggested work

💡 PRODUCTIVITY TIP

Give one short practical suggestion.

Tasks:
{tasks}
"""

REMINDER_PROMPT = """
Analyze the user's tasks and identify tasks that need immediate attention.

Rules:
- Ignore completed tasks.
- Highlight overdue tasks first.
- Then highlight tasks due today.
- Then highlight tasks due within 2 days.
- If there are no urgent tasks, say that clearly.
- Keep the response short and practical.

Use this format:

🔔 DEADLINE REMINDERS

🚨 Urgent:
- Task name — deadline — reason

⚠️ Coming Soon:
- Task name — deadline — reason

💡 Reminder Tip:
Give one short practical suggestion.

Tasks:
{tasks}
"""

AI_TASK_PROMPT = """
Extract a task from the user's sentence.

Return ONLY valid JSON in exactly this format:

{{
    "name": "task name",
    "deadline": "YYYY-MM-DD",
    "priority": "Low"
}}

Rules:

- Extract the task name clearly.
- Convert the deadline to YYYY-MM-DD.
- Priority must be exactly Low, Medium, or High.
- If the user says important, urgent, critical, or very important, use High.
- If the user gives no priority, use Medium.
- Today's date is {today}.
- If no deadline is provided, use today's date.
- Do not include markdown.
- Do not include explanations.

User sentence:
{user_text}
"""

SUBTASK_PROMPT = """
Break the following task into 3 to 6 practical subtasks.

Return ONLY valid JSON in this format:

{{
    "subtasks": [
        "Subtask 1",
        "Subtask 2",
        "Subtask 3"
    ]
}}

Rules:
- Give practical steps.
- Keep each subtask short.
- Do not repeat the main task.
- Do not include markdown.
- Do not include explanations.

Main task:
{task_name}
"""

# ---------------- RISK ANALYSIS PROMPT ----------------

RISK_PROMPT = """
Analyze the user's current tasks and identify deadline risk.

Consider:
- Deadline
- Days remaining
- Priority
- Completed status

Rules:
- Do not include completed tasks.
- Overdue tasks are HIGH RISK.
- Tasks due today are HIGH RISK.
- Tasks due within 2 days are HIGH RISK.
- Tasks due within 4 days may be MEDIUM RISK.
- Tasks with more than 4 days remaining are LOW RISK.
- High-priority tasks should receive extra attention.

Use this format:

🚨 HIGH RISK

Task Name
📅 Deadline: ...
🎯 Priority: ...
⏳ Time remaining: ...
💡 Reason: ...


🟠 MEDIUM RISK

Task Name
📅 Deadline: ...
🎯 Priority: ...
⏳ Time remaining: ...
💡 Reason: ...


🟢 LOW RISK

Task Name
📅 Deadline: ...
🎯 Priority: ...
⏳ Time remaining: ...
💡 Reason: ...

If a category has no tasks, write:
None

Tasks:
{tasks}
"""
import streamlit as st
from datetime import date
from google import genai

from prompts import (
    SYSTEM_PROMPT,
    PRIORITY_PROMPT,
    PLAN_PROMPT,
    REMINDER_PROMPT,
    AI_TASK_PROMPT,
    SUBTASK_PROMPT,
    RISK_PROMPT
)

from database import (
    add_task,
    get_tasks,
    complete_task,
    delete_task,
    update_task
)

# -----------------------------
# Page Configuration
# -----------------------------

st.set_page_config(
    page_title="Deadline Tracker",
    page_icon="📅",
    layout="wide"
)

# ---------------- CUSTOM UI STYLE ----------------

st.markdown("""
<style>

.main-title {
    font-size: 42px;
    font-weight: 700;
    margin-bottom: 5px;
}

.subtitle {
    font-size: 18px;
    color: #666666;
    margin-bottom: 25px;
}

.section-title {
    font-size: 25px;
    font-weight: 600;
    margin-top: 25px;
}

</style>
""", unsafe_allow_html=True)






# -----------------------------
# Gemini Client
# -----------------------------

@st.cache_resource
def get_gemini_client():
    return genai.Client(
        api_key=st.secrets["GEMINI_API_KEY"]
    )


client = get_gemini_client()


# -----------------------------
# Session State
# Only used for chat history
# -----------------------------

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---------------- USER LOGIN ----------------

if "username" not in st.session_state:
    st.session_state.username = None

if st.session_state.username is None:

    st.title("📅 Deadline Tracker")

    st.subheader("👤 Login")

    username = st.text_input(
        "Enter your username",
        placeholder="Example: Pujitha"
    )

    if st.button(
        "🚀 Continue",
        use_container_width=True
    ):

        if username.strip():

            from database import add_user, get_user

            add_user(username.strip())

            user = get_user(username.strip())

            st.session_state.username = username.strip()
            st.session_state.user_id = user["id"]

            st.rerun()

        else:

            st.warning(
                "Please enter your username."
            )

    st.stop()

# ---------------- USER PROFILE ----------------

st.sidebar.markdown(
    "## 📅 Deadline Tracker"
)

st.sidebar.caption(
    "Your personal AI-powered deadline manager"
)

st.sidebar.markdown("### 👤 User")

st.sidebar.write(
    f"Logged in as: **{st.session_state.username}**"
)

if st.sidebar.button(
    "🚪 Logout",
    use_container_width=True
):

    st.session_state.username = None
    st.session_state.user_id = None
    st.session_state.chat_history = []

    st.rerun()


# ---------------- WELCOME MESSAGE ----------------

st.markdown(
    f"### 👋 Welcome, {st.session_state.username}!"
)

st.caption(
    "Manage your deadlines, prioritize your work, and let AI plan your day."
)

# -----------------------------
# Functions
# -----------------------------

def get_status(deadline, completed):

    if completed:
        return "✅ Completed"

    days_left = (deadline - date.today()).days

    if days_left < 0:
        return "🚨 Overdue"

    elif days_left == 0:
        return "🔴 Due Today"

    elif days_left <= 2:
        return "🟠 Urgent"

    elif days_left <= 7:
        return "🟡 Upcoming"

    else:
        return "🟢 Planned"


# -----------------------------
# Header
# -----------------------------

st.markdown(
    '<div class="main-title">📅 Deadline Tracker</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Manage your deadlines smarter with AI.'
    '</div>',
    unsafe_allow_html=True
)

st.write(
    "Track your tasks, deadlines, and priorities in one place."
)

st.divider()

# ---------------- AI TASK CREATOR ----------------

st.markdown(
    '<div class="section-title">'
    '✨ Create Task with AI'
    '</div>',
    unsafe_allow_html=True
)

st.caption(
    "Describe your task naturally and let AI extract the details."
)

ai_task_text = st.text_input(
    "Describe your task",
    placeholder=(
        "Example: Submit DBMS assignment by Monday, "
        "it is very important"
    )
)

if st.button(
    "✨ Extract Task Details",
    use_container_width=True
):

    if ai_task_text.strip():

        prompt = AI_TASK_PROMPT.format(
            today=date.today().isoformat(),
            user_text=ai_task_text
        )

        with st.spinner(
            "🤖 AI is extracting task details..."
        ):

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=(
                    SYSTEM_PROMPT
                    + "\n\n"
                    + prompt
                )
            )

        try:

            import json

            ai_task = json.loads(
                response.text.strip()
            )

            st.session_state.ai_task = ai_task

        except Exception:

            st.error(
                "AI could not understand the task. "
                "Please try again."
            )

    else:

        st.warning(
            "Please describe your task first."
        )


# ---------------- AI TASK PREVIEW ----------------

if "ai_task" in st.session_state:

    ai_task = st.session_state.ai_task

    st.markdown("### 📝 AI Extracted Task")

    st.write(
        f"📌 **Task:** {ai_task['name']}"
    )

    st.write(
        f"📅 **Deadline:** {ai_task['deadline']}"
    )

    st.write(
        f"🎯 **Priority:** {ai_task['priority']}"
    )

    if st.button(
        "➕ Add This Task",
        use_container_width=True
    ):

        add_task(
            st.session_state.user_id,
            ai_task["name"],
            ai_task["deadline"],
            ai_task["priority"]
        )

        del st.session_state.ai_task

        st.success(
            "🎉 Task added successfully!"
        )

        st.rerun()


# ---------------- AI SUBTASK GENERATOR ----------------

st.markdown("---")

st.markdown(
    '<div class="section-title">'
    '🧩 Break Task into Subtasks'
    '</div>',
    unsafe_allow_html=True
)

st.caption(
    "Enter a task and let AI break it into smaller steps."
)

subtask_name = st.text_input(
    "Task for AI to break down",
    placeholder="Example: Complete DBMS project"
)

if st.button(
    "🧩 Generate Subtasks",
    use_container_width=True
):

    if subtask_name.strip():

        prompt = SUBTASK_PROMPT.format(
            task_name=subtask_name.strip()
        )

        with st.spinner(
            "🤖 AI is creating subtasks..."
        ):

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=(
                    SYSTEM_PROMPT
                    + "\n\n"
                    + prompt
                )
            )

        st.session_state.generated_subtasks = (
            response.text
        )

    else:

        st.warning(
            "Please enter a task first."
        )

if "generated_subtasks" in st.session_state:

    st.markdown("### 📋 AI Suggested Subtasks")

    import json

    try:

        subtask_data = json.loads(
            st.session_state.generated_subtasks.strip()
        )

        subtasks = subtask_data["subtasks"]

        # Create checkboxes
        for index, subtask in enumerate(subtasks):

            st.checkbox(
                subtask,
                key=f"subtask_{index}_{subtask}"
            )

        completed_subtasks = sum(
            1
            for index, subtask in enumerate(subtasks)
            if st.session_state.get(
                f"subtask_{index}_{subtask}",
                False
            )
        )

        total_subtasks = len(subtasks)

        if total_subtasks > 0:

            progress = (
                completed_subtasks / total_subtasks
            )

            st.progress(progress)

            st.write(
                f"**{completed_subtasks} of "
                f"{total_subtasks} subtasks completed**"
            )

    except Exception:

        st.error(
            "AI returned an unexpected subtask format. "
            "Please generate the subtasks again."
        )

# -----------------------------
# Add New Task
# -----------------------------

st.markdown(
    '<div class="section-title">➕ Add New Task</div>',
    unsafe_allow_html=True
)

with st.form("task_form"):

    task_name = st.text_input(
        "Task Name",
        placeholder="Example: Submit DBMS Assignment"
    )

    deadline = st.date_input(
        "Deadline",
        min_value=date.today()
    )

    priority = st.selectbox(
        "Priority",
        ["Low", "Medium", "High"]
    )

    submitted = st.form_submit_button("Add Task")

    if submitted:

        if task_name.strip():

            add_task(
                st.session_state.user_id,
                task_name.strip(),
                deadline,
                priority
            )

            st.success(
                "Task added successfully! 🎉"
            )

        else:

            st.warning(
                "Please enter a task name."
            )


# -----------------------------
# Get Tasks From Database
# -----------------------------

tasks = get_tasks(st.session_state.user_id)

# ---------------- AI TASK INFORMATION ----------------

task_text = ""

for task in tasks:

    task_deadline = date.fromisoformat(
        task["deadline"]
    )

    days_left = (
        task_deadline - date.today()
    ).days

    task_text += f"""
Task: {task["name"]}
Deadline: {task["deadline"]}
Priority: {task["priority"]}
Days remaining: {days_left}
Completed: {task["completed"]}
---
"""

# ---------------- AUTOMATIC DEADLINE ALERTS ----------------

urgent_tasks = []

for task in tasks:

    if task["completed"]:
        continue

    task_deadline = date.fromisoformat(
        task["deadline"]
    )

    days_left = (
        task_deadline - date.today()
    ).days

    if days_left <= 2:
        urgent_tasks.append(
            (task, days_left)
        )

# ---------------- ALERT DISPLAY ----------------

if urgent_tasks:

    st.markdown("### 🚨 Deadline Alerts")

    for task, days_left in urgent_tasks:

        if days_left < 0:

            st.error(
                f"🚨 **{task['name']}** is overdue!  "
                f"Deadline: {task['deadline']}"
            )

        elif days_left == 0:

            st.error(
                f"🔴 **{task['name']}** is due TODAY!  "
                f"Priority: {task['priority']}"
            )

        elif days_left == 1:

            st.warning(
                f"🟠 **{task['name']}** is due TOMORROW!  "
                f"Priority: {task['priority']}"
            )

        else:

            st.warning(
                f"🟡 **{task['name']}** is due in "
                f"{days_left} days!  "
                f"Priority: {task['priority']}"
            )

st.divider()


# -----------------------------
# Dashboard
# -----------------------------

st.markdown(
    '<div class="section-title">📊 Dashboard</div>',
    unsafe_allow_html=True
)

total_tasks = len(tasks)

completed_tasks = sum(
    1 for task in tasks
    if task["completed"]
)

pending_tasks = total_tasks - completed_tasks

overdue_tasks = sum(
    1 for task in tasks
    if not task["completed"]
    and date.fromisoformat(task["deadline"]) < date.today()
)

upcoming_tasks = sum(
    1 for task in tasks
    if not task["completed"]
    and date.fromisoformat(task["deadline"]) >= date.today()
)

# Completion percentage
if total_tasks > 0:
    completion_percentage = completed_tasks / total_tasks
else:
    completion_percentage = 0


# Dashboard metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "📋 Total Tasks",
        total_tasks
    )

with col2:
    st.metric(
        "⏳ Pending",
        pending_tasks
    )

with col3:
    st.metric(
        "🚨 Overdue",
        overdue_tasks
    )

with col4:
    st.metric(
        "✅ Completed",
        completed_tasks
    )


# Progress
st.markdown("### 📈 Overall Progress")

st.progress(
    completion_percentage
)

st.write(
    f"**{completed_tasks} of {total_tasks} tasks completed "
    f"({completion_percentage * 100:.0f}%)**"
)
# -----------------------------
# PRIORITY SUMMARY
# -----------------------------

st.markdown("### 🎯 Priority Summary")

high_priority = sum(
    1
    for task in tasks
    if not task["completed"]
    and task["priority"] == "High"
)

medium_priority = sum(
    1
    for task in tasks
    if not task["completed"]
    and task["priority"] == "Medium"
)

low_priority = sum(
    1
    for task in tasks
    if not task["completed"]
    and task["priority"] == "Low"
)

priority_col1, priority_col2, priority_col3 = st.columns(3)

with priority_col1:
    st.metric(
        "🔴 High Priority",
        high_priority
    )

with priority_col2:
    st.metric(
        "🟡 Medium Priority",
        medium_priority
    )

with priority_col3:
    st.metric(
        "🟢 Low Priority",
        low_priority
    )
st.markdown("### 🎯 Today's Focus")

today_tasks = []

for task in tasks:
    task_deadline = date.fromisoformat(task["deadline"])

    if (
        not task["completed"]
        and task_deadline <= date.today()
    ):
        today_tasks.append(task)


if today_tasks:

    for task in today_tasks:

        task_deadline = date.fromisoformat(
            task["deadline"]
        )

        status = get_status(
            task_deadline,
            task["completed"]
        )

        st.warning(
            f"**{task['name']}**  \n"
            f"📅 Deadline: {task['deadline']}  \n"
            f"🎯 Priority: {task['priority']}  \n"
            f"{status}"
        )

else:

    st.success(
        "🎉 No urgent tasks for today!"
    )
# -----------------------------
# Task List
# -----------------------------

st.subheader("📝 My Tasks")


# Task filter

filter_option = st.selectbox(
    "🔍 Filter Tasks",
    [
        "All",
        "Upcoming",
        "Urgent",
        "Overdue",
        "Completed"
    ]
)


# Filter tasks

filtered_tasks = []

for task in tasks:

    task_deadline = date.fromisoformat(
        task["deadline"]
    )

    days_left = (
        task_deadline - date.today()
    ).days

    completed = task["completed"]


    if filter_option == "All":
        filtered_tasks.append(task)

    elif filter_option == "Completed":
        if completed:
            filtered_tasks.append(task)

    elif filter_option == "Overdue":
        if not completed and days_left < 0:
            filtered_tasks.append(task)

    elif filter_option == "Urgent":
        if not completed and 0 <= days_left <= 2:
            filtered_tasks.append(task)

    elif filter_option == "Upcoming":
        if not completed and days_left >= 0:
            filtered_tasks.append(task)
st.write(
    f"Showing {len(filtered_tasks)} task(s)"
)

# Display tasks

if not filtered_tasks:

    st.info("No tasks found for this filter.")

else:

    for task in filtered_tasks:

        task_id = task["id"]

        task_deadline = date.fromisoformat(
            task["deadline"]
        )

        days_left = (
            task_deadline - date.today()
        ).days

        status = get_status(
            task_deadline,
            task["completed"]
        )


        with st.container(border=True):

            col1, col2, col3 = st.columns(
                [4, 2, 2]
            )


            # Task details

            with col1:

                st.markdown(
                    f"""
                    <div style="
                        padding: 15px;
                        border-radius: 12px;
                        border: 1px solid #ddd;
                        margin-bottom: 10px;
                    ">
                        <h3>📌 {task['name']}</h3>
                        <p>📅 <b>Deadline:</b> {task['deadline']}</p>
                        <p>🎯 <b>Priority:</b> {task['priority']}</p>
                        <p>{status}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )


            # Status

            with col2:

                st.write(
                    f"**Status:** {status}"
                )

                if task["completed"]:

                    st.write(
                        "Task completed 🎉"
                    )

                elif days_left < 0:

                    st.write(
                        f"Overdue by **{abs(days_left)} days**"
                    )

                elif days_left == 0:

                    st.write(
                        "Due **today!**"
                    )

                else:

                    st.write(
                        f"**{days_left} days** remaining"
                    )


            # Buttons

            with col3:

                if not task["completed"]:

                    if st.button(
                        "✅ Complete",
                        key=f"complete_{task_id}"
                    ):

                        complete_task(
                                task_id,
                                st.session_state.user_id
                            )
                        st.rerun()


                if st.button(
                    "✏️ Edit",
                    key=f"edit_{task_id}"
                ):

                    st.session_state[
                        f"editing_{task_id}"
                    ] = True


                if st.button(
                    "🗑️ Delete",
                    key=f"delete_{task_id}"
                ):

                    delete_task(
                        task_id,
                        st.session_state.user_id
                    )

                    st.rerun()
                                # Edit form

            if st.session_state.get(
                f"editing_{task_id}",
                False
            ):

                st.divider()

                st.write("✏️ **Edit Task**")

                with st.form(
                    f"edit_form_{task_id}"
                ):

                    edited_name = st.text_input(
                        "Task Name",
                        value=task["name"]
                    )

                    edited_deadline = st.date_input(
                        "Deadline",
                        value=task_deadline
                    )

                    edited_priority = st.selectbox(
                        "Priority",
                        ["Low", "Medium", "High"],
                        index=[
                            "Low",
                            "Medium",
                            "High"
                        ].index(task["priority"])
                    )

                    save_edit = st.form_submit_button(
                        "💾 Save Changes"
                    )

                    if save_edit:

                        if edited_name.strip():

                            update_task(
                                task_id,
                                st.session_state.user_id,
                                edited_name.strip(),
                                edited_deadline,
                                edited_priority
                            )

                            st.session_state[
                                f"editing_{task_id}"
                            ] = False

                            st.success(
                                "Task updated successfully! 🎉"
                            )

                            st.rerun()

                        else:

                            st.warning(
                                "Task name cannot be empty."
                            )

# -----------------------------
# AI RISK ANALYSIS
# -----------------------------

st.divider()

st.markdown(
    '<div class="section-title">'
    '🚨 AI Deadline Risk Analysis'
    '</div>',
    unsafe_allow_html=True
)

st.caption(
    "Let AI identify which tasks have the highest deadline risk."
)

if st.button(
    "🚨 Analyze Deadline Risk",
    use_container_width=True
):

    if not tasks:

        st.info(
            "Add some tasks first, then analyze deadline risk."
        )

    else:

        with st.spinner(
            "🤖 AI is analyzing deadline risks..."
        ):

            prompt = RISK_PROMPT.format(
                tasks=task_text
            )

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=(
                    SYSTEM_PROMPT
                    + "\n\n"
                    + prompt
                )
            )

        st.markdown(
            "### 🚨 AI Risk Report"
        )

        st.markdown(
            response.text
        )

# -----------------------------
# AI DAILY / WEEKLY PLAN
# -----------------------------

st.divider()

st.markdown(
    '<div class="section-title">'
    '📅 AI Daily / Weekly Planner'
    '</div>',
    unsafe_allow_html=True
)

st.caption(
    "Let AI create a practical plan based on your deadlines."
)

if st.button(
    "📅 Generate My Plan",
    use_container_width=True
):

    if not tasks:

        st.info(
            "Add some tasks first, then generate your plan."
        )

    else:

        with st.spinner(
            "🤖 AI is creating your work plan..."
        ):

            prompt = PLAN_PROMPT.format(
                tasks=task_text
            )

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=(
                    SYSTEM_PROMPT
                    + "\n\n"
                    + prompt
                )
            )

        st.markdown(
            "### 📅 Your AI Work Plan"
        )

        st.markdown(
            response.text
        )

# -----------------------------
# AI Deadline Assistant
# -----------------------------

st.divider()

st.markdown(
    '<div class="section-title">'
    '🤖 AI Deadline Assistant'
    '</div>',
    unsafe_allow_html=True
)

st.caption(
    "Ask me about your tasks, priorities, deadlines, or daily plan."
)


if tasks:

    task_text = ""


    for task in tasks:

        task_deadline = date.fromisoformat(
            task["deadline"]
        )

        days_left = (
            task_deadline - date.today()
        ).days


        task_text += f"""
Task: {task["name"]}
Deadline: {task["deadline"]}
Priority: {task["priority"]}
Days remaining: {days_left}
Completed: {task["completed"]}
---
"""


    col1, col2 = st.columns(2)

    # AI Priority Analysis
    with col1:
        if st.button(
            "🧠 Analyze My Tasks",
            use_container_width=True,
        ):
            prompt = PRIORITY_PROMPT.format(
                tasks=task_text
            )

            with st.spinner(
                "🤖 AI is analyzing your deadlines..."
            ):
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=(
                        SYSTEM_PROMPT
                        + "\n\n"
                        + prompt
                    )
                )

            st.markdown(
                "### 📌 AI Priority Analysis"
            )
            st.markdown(
                response.text
            )

        


else:

    st.info(
        "Add some tasks first, then ask the AI to analyze them."
    )


st.markdown("---")

st.markdown(
    '<div class="section-title">🔔 AI Deadline Reminders</div>',
    unsafe_allow_html=True
)

if st.button(
    "🔔 Check My Reminders",
    use_container_width=True
):

    prompt = REMINDER_PROMPT.format(
        tasks=task_text
    )

    with st.spinner(
        "🤖 AI is checking your deadlines..."
    ):

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=(
                SYSTEM_PROMPT
                + "\n\n"
                + prompt
            )
        )

    st.markdown(response.text)

# -----------------------------
# AI Chatbot
# -----------------------------

st.divider()

st.subheader(
    "💬 Ask Your Deadline Assistant"
)


# Display previous messages

for message in st.session_state.chat_history:

    with st.chat_message(
        message["role"]
    ):

        st.write(
            message["content"]
        )


# Chat input

user_question = st.chat_input(
    "Ask something about your deadlines..."
)


if user_question:

    # Add user message

    st.session_state.chat_history.append(
        {
            "role": "user",
            "content": user_question
        }
    )


    with st.chat_message("user"):

        st.write(
            user_question
        )


    # Prepare task information

    task_text = ""


    for task in tasks:

        task_deadline = date.fromisoformat(
            task["deadline"]
        )

        days_left = (
            task_deadline - date.today()
        ).days


        task_text += f"""
Task: {task["name"]}
Deadline: {task["deadline"]}
Priority: {task["priority"]}
Days remaining: {days_left}
Completed: {task["completed"]}
---
"""


    chatbot_prompt = f"""
You are an AI Deadline Assistant.

The user is asking about their deadlines.

User's current tasks:

{task_text}

User's question:

{user_question}

Instructions:

1. Use only the user's current tasks when discussing their deadlines.
2. Do not invent tasks.
3. Ignore completed tasks when recommending work.
4. Identify overdue tasks clearly.
5. Identify tasks due today clearly.
6. Consider both deadline and priority.
7. Give practical and short advice.
8. If the user asks what to do first, explain why you selected that task.
9. If there are no tasks, tell the user to add a task.
10. If the question is unrelated to deadlines, answer briefly.

Give a clear, friendly response.
"""


    # Generate AI response

    with st.chat_message("assistant"):

        with st.spinner("🤖 Thinking..."):

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=(
                    SYSTEM_PROMPT
                    + "\n\n"
                    + chatbot_prompt
                )
            )


            answer = response.text


        st.write(answer)


    # Save assistant message

    st.session_state.chat_history.append(
        {
            "role": "assistant",
            "content": answer
        }
    )
    st.rerun()
📅 Deadline Tracker – README
An AI-powered task and deadline management application built with Streamlit and Google Gemini.

🚀 Overview
Deadline Tracker helps users organize their tasks, track deadlines, prioritize important work, and reduce the risk of missing deadlines.
Users can create tasks manually or use AI to extract task details from natural language. The application also provides AI-powered subtasks, priority analysis, reminders, risk analysis, and daily/weekly planning.

✨ Features
•	👤 User login and logout
•	➕ Add tasks manually
•	✏️ Edit tasks
•	✅ Complete tasks
•	🗑️ Delete tasks
•	🔍 Filter and search tasks
•	📊 Dashboard with task statistics
•	🎯 Priority management
•	🚨 Automatic deadline alerts
•	🤖 AI Task Creator
•	📋 AI Subtask Generator
•	🔥 AI Priority Analysis
•	🔔 AI Deadline Reminders
•	🚨 AI Deadline Risk Analysis
•	📅 AI Daily/Weekly Planner
•	💬 AI Deadline Assistant chatbot
•	💾 SQLite database

🛠️ Technologies Used
•	Python
•	Streamlit
•	Google Gemini API
•	SQLite
•	Git & GitHub

📁 Project Structure
DeadlineTracker/
│
├── app.py
├── database.py
├── prompts.py
├── requirements.txt
├── README.md
├── .gitignore
│
└── .streamlit/
    └── secrets.toml
Note: secrets.toml contains the Gemini API key and should never be committed to GitHub.

⚙️ Setup Instructions
1. Clone the repository
git clone https://github.com/Rampujitha-123/DeadlineTracker.git
cd DeadlineTracker
2. Create a virtual environment
python -m venv venv
3. Activate the virtual environment
Windows:
venv\Scripts\activate
macOS/Linux:
source venv/bin/activate
4. Install dependencies
pip install -r requirements.txt
5. Configure the Gemini API key
Create the following file: .streamlit/secrets.toml
Add the following content:
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
Replace YOUR_GEMINI_API_KEY with your actual Gemini API key. Never upload your API key to GitHub.
6. Run the application
python -m streamlit run app.py
The application will open in your browser at: http://localhost:8501

🌐 Live Demo
    https://deadlinetracker-nhknnkqpbuhnbiyiswazpm.streamlit.app/

🔐 Security
The Gemini API key is stored using Streamlit secrets and is excluded from Git using .gitignore.
The following files are not committed:
•	.streamlit/secrets.toml
•	deadlines.db
•	venv/

🎯 Future Improvements
•	☁️ Cloud database integration
•	👥 Multi-user authentication
•	📧 Email notifications
•	📱 Mobile application
•	📈 Advanced productivity analytics
•	🔄 Cloud data synchronization

👩‍💻 Author
Nidamanuri Ram pujitha
GitHub: https://github.com/Rampujitha-123

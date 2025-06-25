# 🧪 AI Test Case Generator

A Streamlit-based AI tool for generating manual and automated test cases using OpenAI.  
Supports BDD, data-driven, POM, and keyword-driven styles. Built by [Vitus Idi](https://github.com/galapoto).

## 🚀 Features

- 🔐 Firebase login and session persistence
- ✍️ Generate test cases from user stories
- 🧱 Choose framework and style (e.g. Robot Framework, BDD)
- 📥 Download .txt and .csv
- 📤 Share via email or copy to clipboard
- 📚 Project history with saved outputs

## 🧰 Tech Stack

- Streamlit
- OpenAI API
- Firebase Auth (via Pyrebase)
- Python 3.10+
- Pandas

## 🔧 Setup

```bash
git clone https://github.com/your-username/ai-testcase-generator.git
cd ai-testcase-generator
python -m venv venv
source venv/bin/activate  # or venv\\Scripts\\activate on Windows
pip install -r requirements.txt
Run the app:
streamlit run app.py

Gmail API Setup
Go to https://console.cloud.google.com/

Create a project, enable Gmail API

Create OAuth Client ID for Desktop

Download credentials.json into project root

On first run, authenticate in browser

---

## ✅ PHASE 3: Add Versioning to Projects

Inside the `"saved_projects"` JSON, you already store timestamps — we’ll allow saving multiple versions by simply appending new ones.

➡️ Already implemented via:
```python
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


---

## ✅ 4. `requirements.txt` (generate locally)

In your terminal, run:

```bash
pip freeze > requirements.txt

This will capture packages like:

streamlit
openai
pyrebase4
python-dotenv
pandas

5. .streamlit/secrets.toml (local use only)
# .streamlit/secrets.toml

FIREBASE_API_KEY = "your-api-key"
FIREBASE_AUTH_DOMAIN = "your-app.firebaseapp.com"
FIREBASE_PROJECT_ID = "your-app-id"
FIREBASE_STORAGE_BUCKET = "your-app.appspot.com"
FIREBASE_MESSAGING_SENDER_ID = "your-sender-id"
FIREBASE_APP_ID = "your-app-id"
FIREBASE_MEASUREMENT_ID = "your-measurement-id"

OPENAI_API_KEY = "your-openai-key"

# Footer
st.markdown(f'''
<div style="display: flex; justify-content: space-between; align-items: center; margin-top: 50px;">
    <div style="display: flex; align-items: center;">
        <span>
            Created by <a href="https://github.com/galapoto/test-case-generator.git" target="_blank">
            <strong>Vitus Idi</strong></a>
        </span>
        <img src="data:image/png;base64,{img_base64}" alt="Vitus" width="40"
             style="border-radius: 50%; margin-left: 10px;">
    </div>
</div>
''', unsafe_allow_html=True)
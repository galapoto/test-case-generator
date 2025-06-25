# 🧪 AI Test Case Generator

A Streamlit-based AI tool built for generating manual and automated test cases using OpenAI.  
Supports BDD, data-driven, POM, and keyword-driven styles.

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

## 🔧 Setup

```bash
git clone https://github.com/your-username/ai-testcase-generator.git
cd ai-testcase-generator
python -m venv venv
source venv/bin/activate  
pip install -r requirements.txt
streamlit run app.py
```


Gmail API Setup
Go to (https://console.cloud.google.com/)

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
```



## ✅ 4. `requirements.txt` (generate locally)

In your terminal, run:

pip freeze > requirements.txt

This will capture packages like:

streamlit
openai
pyrebase4
python-dotenv
pandas

---
## .streamlit/secrets.toml

FIREBASE_API_KEY = "your-api-key"
FIREBASE_AUTH_DOMAIN = "your-app.firebaseapp.com"
FIREBASE_PROJECT_ID = "your-app-id"
FIREBASE_STORAGE_BUCKET = "your-app.appspot.com"
FIREBASE_MESSAGING_SENDER_ID = "your-sender-id"
FIREBASE_APP_ID = "your-app-id"
FIREBASE_MEASUREMENT_ID = "your-measurement-id"

OPENAI_API_KEY = "your-openai-key"

---

Streamlit Cloud Deployment
1. Create a GitHub repo

2. Push your files

3. Create a new app at Streamlit Cloud

4. Add your secrets.toml values under Settings → Secrets

5. Upload credentials.json + token.json via Secrets > Files

---

Folder Structure
├── app.py
├── prompts.py
├── firebase_auth.py
├── memory.py
├── utils.py
├── image_base64.py
├── .streamlit/secrets.toml
├── requirements.txt
├── credentials.json / token.json

---

Memory and Versioning
Test cases are saved in saved_projects/ as JSON and versioned by timestamp.
Lightweight local memory is stored in vector_data.json for search and filters

---

☁️ Deploying to Streamlit Cloud
Push this repo to GitHub
1. reate a new app on streamlit.io/cloud
2. Set entry point to app.py
3. Paste your secrets into Settings > Secrets
4. Upload credentials.json and token.json into Secrets > Files

---

## 👤 Created by

![Vitus Idi](images/avatar-fixed.png)

**Vitus Idi**  
🔗 [GitHub Repository](https://github.com/galapoto/test-case-generator)

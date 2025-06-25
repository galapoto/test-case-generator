from openai import OpenAI
import streamlit as st
import os
from dotenv import load_dotenv
import pandas as pd
import datetime
from image_base64 import img_base64, openai_logo_base64
import re
import json
import urllib.parse
import base64
from email.message import EmailMessage
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from collections import defaultdict
from prompts import get_prompt
from firebase_auth import init_firebase, login_ui
from memory import load_vector_data, append_vector_entry, save_vector_data
from utils import render_output, send_email_with_attachment

# --- Session State Init ---
for key in ["user", "login_error", "export_ready", "send_email_triggered"]:
    if key not in st.session_state:
        st.session_state[key] = False if key != "user" else None

# --- Firebase Auth ---
auth = init_firebase()
if not st.session_state.user:
    login_ui(auth)
    if st.session_state.login_error:
        st.error("Login failed. Check credentials.")
    st.stop()
if st.session_state.user and not st.session_state.get("just_logged_in_shown", False):
    st.success("Logged in successfully!")
    st.session_state.just_logged_in_shown = True

# --- Inlined Prompt Generator ---
def get_prompt(user_story, test_type, format_type, expected_result, severity, category, framework, style):
    prompt = f"""You are an expert software tester.

Generate {test_type.lower()} test cases for the following feature.

Feature/User Story:
{user_story}

Output Format:
{format_type}
"""

    if format_type != "Manual Only":
        prompt += f"""
Preferred Automation Framework:
{framework}

Preferred Automation Style:
{style}
"""

    if expected_result:
        prompt += f"\nExpected Result:\n{expected_result}"
    if severity:
        prompt += f"\nSeverity: {severity}"
    if category:
        prompt += f"\nCategory: {category}"

    prompt += """

Respond with clearly labeled sections.
If format is 'Manual Only', do not include any code.
If automation is included, use code blocks with appropriate labels.
"""

    return prompt


# --- Utilities ---
def render_output(output):
    pattern = re.compile(r"```(\w+)?\n(.*?)```", re.DOTALL)
    for match in pattern.finditer(output):
        lang = match.group(1) or "text"
        code = match.group(2).strip()
        st.code(code, language=lang)

# --- Gmail API ---
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def send_email_with_attachment(to_email, subject, body_text, file_path):
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    service = build('gmail', 'v1', credentials=creds)
    message = EmailMessage()
    message.set_content(body_text)
    message['To'] = to_email
    message['From'] = "me"
    message['Subject'] = subject
    with open(file_path, 'rb') as f:
        file_data = f.read()
        file_name = os.path.basename(file_path)
    message.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    create_message = {'raw': encoded_message}
    service.users().messages().send(userId='me', body=create_message).execute()

# --- Firebase Auth ---
firebase_config = {
    "apiKey": st.secrets["FIREBASE_API_KEY"],
    "authDomain": st.secrets["FIREBASE_AUTH_DOMAIN"],
    "projectId": st.secrets["FIREBASE_PROJECT_ID"],
    "storageBucket": st.secrets["FIREBASE_STORAGE_BUCKET"],
    "messagingSenderId": st.secrets["FIREBASE_MESSAGING_SENDER_ID"],
    "appId": st.secrets["FIREBASE_APP_ID"],
    "measurementId": st.secrets["FIREBASE_MEASUREMENT_ID"],
    "databaseURL": ""
}

firebase = init_firebase()  # ✅ Replace direct call to pyrebase here
auth = firebase.auth()

# --- Session State Init ---
for key in ["user", "login_error", "export_ready"]:
    if key not in st.session_state:
        st.session_state[key] = None if key == "user" else False

# --- Login UI ---
def login_ui():
    st.title("🔑 Login to AI Test Case Generator")
    choice = st.selectbox("Login or Signup", ["Login", "Sign up"])
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if choice == "Login":
        if st.button("Login"):
            try:
                user = auth.sign_in_with_email_and_password(email, password)
                st.session_state.user = user
                st.session_state.login_error = False
                st.rerun()
            except:
                st.session_state.login_error = True
                st.rerun()
    else:
        if st.button("Sign up"):
            try:
                user = auth.create_user_with_email_and_password(email, password)
                st.success("Account created. Now log in.")
            except:
                st.error("Signup failed. Try different email or stronger password.")

if not st.session_state.user:
    login_ui()
    if st.session_state.login_error:
        st.error("Login failed. Check credentials.")
    st.stop()

if st.session_state.user and not st.session_state.get("just_logged_in_shown", False):
    st.success("Logged in successfully!")
    st.session_state.just_logged_in_shown = True

# --- Load API ---
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- UI Layout ---
st.set_page_config(page_title="AI Test Case Generator")
st.title("🧪 AI Test Case Generator")

# --- Sidebar History ---
st.sidebar.header("📂 Project History")
st.sidebar.write(f"Logged in as: {st.session_state.user['email']}")
if st.sidebar.button("🔄 Refresh History"):
    st.rerun()

project_groups = defaultdict(list)

st.markdown("### 🔎 Search & Filter Your Projects")

search_query = st.text_input("🔍 Search by keywords (story or test case)")
filter_title = st.text_input("📌 Filter by Project Title")
filter_type = st.selectbox("🎯 Filter by Test Type", ["", "Functional", "Negative", "BDD (Gherkin)"])

if os.path.exists("saved_projects"):
    for filename in os.listdir("saved_projects"):
        if filename.endswith(".json"):
            with open(f"saved_projects/{filename}", encoding="utf-8") as f:
                data = json.load(f)
            if data.get("author_email") == st.session_state.user["email"]:
                project_groups[data["title"]].append((data["timestamp"], filename, data))

for title, versions in sorted(project_groups.items()):
    with st.sidebar.expander(f"📂 {title} ({len(versions)} versions)", expanded=False):
        for timestamp, filename, data in sorted(versions, reverse=True):
            st.markdown(f"- 🕒 {timestamp}")
            st.markdown(f"  - 🧪 **Type**: {data['format_type']}, {data['test_type']}")
            st.markdown(f"  - 🧱 **Framework**: {data.get('framework', '-')}")
            anchor_id = f"id_{filename.replace('.', '')}"
            st.markdown(f"  - 📌 [View Output](#{anchor_id})")

# --- Inputs ---
project_title = st.text_input("📌 Project Title")
author_name = st.text_input("✍️ Author Name", value=st.session_state.user["email"])
user_story = st.text_area("📝 Feature/User Story")

test_type = st.selectbox("🎯 Test Case Style", ["Functional", "Negative", "BDD (Gherkin)"])
format_type = st.selectbox("🧪 Output Format", ["Manual Only", "Automation Only", "Both"])
framework = style = ""
if format_type != "Manual Only":
    framework = st.selectbox("🧱 Automation Framework", ["Robot Framework", "Cypress", "Cucumber", "Playwright"])
    style = st.selectbox("⚙️ Automation Style", ["BDD", "Data-Driven", "Page Object Model", "Keyword-Driven"])

expected_result = st.text_input("✅ Expected Result (optional)")
severity = st.selectbox("⚠️ Severity", ["", "Low", "Medium", "High", "Critical"])
category = st.selectbox("🧩 Test Category", ["", "Regression", "Smoke", "Integration", "System", "Exploratory"])

# --- Generate Output ---
if st.button("Generate"):
    if not project_title.strip() or not author_name.strip() or not user_story.strip():
        st.warning("Please complete all required fields.")
    else:
        with st.spinner("Generating test assets..."):
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            prompt = get_prompt(
                user_story, test_type, format_type,
                expected_result, severity, category,
                framework, style
            )
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4
            )
            output = response.choices[0].message.content
            render_output(output)
            st.markdown(f"### ✨ Output for {format_type}")

            # --- Store current project in session state
            st.session_state.output = output
            st.session_state.project_title = project_title
            st.session_state.timestamp = timestamp
            st.session_state.format_type = format_type
            st.session_state.export_ready = True

            # --- Save project as .json file
            os.makedirs("saved_projects", exist_ok=True)
            project_data = {
                "title": project_title,
                "author": author_name,
                "author_email": st.session_state.user["email"],
                "timestamp": timestamp,
                "test_type": test_type,
                "format_type": format_type,
                "framework": framework,
                "style": style,
                "expected_result": expected_result,
                "severity": severity,
                "category": category,
                "user_story": user_story,
                "output": output
            }
            with open(f"saved_projects/{project_title}_{timestamp}.json", "w", encoding="utf-8") as f:
                json.dump(project_data, f, indent=2)

            st.success("✅ Project saved.")

            # --- Load existing vector_data for filtering
            vector_data = []
            if os.path.exists("vector_data.json"):
                with open("vector_data.json", "r", encoding="utf-8") as f:
                    vector_data = json.load(f)

            # --- Filter/Search Results
            filtered_results = []

            for entry in vector_data:
                if filter_title and filter_title.lower() not in entry['title'].lower():
                    continue
                if filter_type and entry.get("test_type", "").lower() != filter_type.lower():
                    continue
                if search_query and search_query.lower() not in (entry['output'] + entry['title']).lower():
                    continue
                filtered_results.append(entry)

            st.markdown(f"### 🎯 Filtered Results ({len(filtered_results)})")
            for data in filtered_results:
                st.markdown(f"📝 **{data['title']}** @ {data['timestamp']}")
                st.code(data["output"][:400] + "...")

# --- Export Section (always rendered if available) ---
if st.session_state.get("export_ready", False):
    st.markdown("### 📤 Export and Share")
    with st.expander("📧 Preview Email Body", expanded=False):
        st.code("See the test output below:\n\n" + st.session_state.output[:1500], language="text")

    mailto = f"mailto:?subject=Test Cases Generated&body={urllib.parse.quote('See the test output below:\n\n' + st.session_state.output[:1500])}"
    st.code(mailto, language="text")
    st.markdown("Click or copy the link above to share via email.")
    st.markdown(f'<a href="{mailto}" target="_blank">🔗 Share via Email</a>', unsafe_allow_html=True)

    # --- Handle button-triggered email send across rerun ---
    recipient_email = st.text_input("📧 Recipient Email", value=st.session_state.user["email"])

    if "send_email_triggered" not in st.session_state:
        st.session_state.send_email_triggered = False

    if st.button("📤 Send via Gmail", key="send_gmail_button"):
        st.session_state.recipient_email = recipient_email
        st.session_state.send_email_triggered = True
        st.rerun()

    if st.session_state.send_email_triggered:
        try:
            filename = f"{st.session_state.project_title}_{st.session_state.timestamp}.txt"
            filepath = os.path.join("saved_projects", filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(st.session_state.output)

            send_email_with_attachment(
                to_email=st.session_state.recipient_email,
                subject="Your Test Cases",
                body_text="Attached is your generated test output.",
                file_path=filepath
            )
            st.success("📧 Email sent successfully!")
        except Exception as e:
            st.error(f"❌ Failed to send email: {e}")
        st.session_state.send_email_triggered = False

    filename_base = f"testcases_{st.session_state.format_type.lower()}_{st.session_state.timestamp}"
    st.download_button("⬇️ Download Output", st.session_state.output, file_name=f"{st.session_state.project_title}.txt", key="download_txt")
    rows = [line for line in st.session_state.output.strip().split("\n") if line.strip() and line[0].isdigit()]
    if rows:
        df = pd.DataFrame({"Test Case": rows})
        st.download_button("⬇️ Download CSV", df.to_csv(index=False), file_name=f"{st.session_state.project_title}.csv", key="download_csv")

# --- Saved Projects Viewer ---
if os.path.exists("saved_projects"):
    for filename in sorted(os.listdir("saved_projects"), reverse=True):
        if filename.endswith(".json"):
            with open(f"saved_projects/{filename}", encoding="utf-8") as f:
                data = json.load(f)
            if data.get("author_email") == st.session_state.user["email"]:
                st.markdown(f"<div id='id_{filename.replace('.', '')}'></div>", unsafe_allow_html=True)
                st.markdown(f"""💡
                <div style="font-size: 16px; margin-top: 1em;">
                    <strong>{data['title']}</strong><br>
                    by <span style="color:#00AEEF;">{data['author'].split('@')[0].capitalize()}</span>
                    <span style="font-size: 12px; color:gray;">({data['timestamp']})</span>
                </div>
                """, unsafe_allow_html=True)
                st.markdown(f"**Test Type**: {data['test_type']} | **Framework**: {data.get('framework', '-')} | **Style**: {data.get('style', '-')}")
                st.markdown(f"**User Story:**\n> {data['user_story']}")
                st.code(data['output'], language="robotframework")
                st.download_button("⬇️ Download Output", data['output'], file_name=f"{data['title']}_{data['timestamp']}.txt", key=f"download_{filename}")
                # Share link generation
                share_path = f"saved_projects/share_{st.session_state.project_title}_{st.session_state.timestamp}.txt"
                with open(share_path, "w", encoding="utf-8") as f:
                    f.write(st.session_state.output)

                share_link = f"file://{os.path.abspath(share_path)}"
                st.markdown("📤 Copyable Share Link:")
                st.code(share_link, language="text")

                st.divider()

# --- Footer ---
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
    <div style="display: flex; align-items: center;">
        <span>
            Powered by <a href="https://openai.com" target="_blank"><strong>OpenAI</strong></a>
        </span>
        <img src="data:image/png;base64,{openai_logo_base64}" alt="OpenAI" width="32"
             style="margin-left: 10px;">
    </div>
</div>
''', unsafe_allow_html=True)
# --- End of app.py --- 


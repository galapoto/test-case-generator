import streamlit as st
import re
import os
import base64
from email.message import EmailMessage
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

def render_output(output):
    pattern = re.compile(r"```(\w+)?\n(.*?)```", re.DOTALL)
    for match in pattern.finditer(output):
        lang = match.group(1) or "text"
        code = match.group(2).strip()
        st.code(code, language=lang)

def send_email_with_attachment(to_email, subject, body_text, file_path):
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
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
import streamlit as st
import pyrebase

def init_firebase():
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
    firebase = pyrebase.initialize_app(firebase_config)
    return firebase.auth()

def login_ui(auth):
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
                auth.create_user_with_email_and_password(email, password)
                st.success("Account created. Now log in.")
            except:
                st.error("Signup failed. Try different email or stronger password.")
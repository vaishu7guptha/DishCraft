import streamlit as st
import bcrypt
import json
import os

USER_FILE = "users.json"

def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return json.load(f)
    return {}

def save_user(username, name, password):
    users = load_users()
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    users[username] = {"name": name, "password": hashed_pw}
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

def authenticate(username, password):
    users = load_users()
    if username in users:
        stored_pw = users[username]["password"].encode()
        return bcrypt.checkpw(password.encode(), stored_pw)
    return False

def login_page():
    # Redirect if already logged in
    if st.session_state.get('logged_in'):
        st.session_state.current_page = "Home"
        st.rerun()
    
    st.markdown("""
    <style>
    .auth-container {
        min-height: 80vh;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 2rem;
    }
    .auth-card {
        background: var(--card);
        padding: 2.5rem;
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        width: 100%;
        max-width: 400px;
        text-align: center;
    }
    .auth-title {
        color: var(--primary);
        font-size: 2rem;
        margin-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="auth-container"><div class="auth-card">', unsafe_allow_html=True)
        
        # Login/Signup Toggle
        auth_mode = st.radio("Choose Mode:", ["Sign In", "Sign Up"], horizontal=True, label_visibility="collapsed")
        
        # Authentication Form
        with st.form("auth_form"):
            if auth_mode == "Sign Up":
                full_name = st.text_input("Full Name", placeholder="John Doe")
                email = st.text_input("Email", placeholder="john@example.com")
                
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            
            if auth_mode == "Sign Up":
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="••••••••")
            
            if st.form_submit_button(f"{auth_mode}"):
                if auth_mode == "Sign In":
                    if authenticate(username, password):
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.current_page = "Home"
                        st.rerun()
                    else:
                        st.error("Invalid credentials!")
                else:
                    if password != confirm_password:
                        st.error("Passwords don't match!")
                    else:
                        save_user(username, full_name, password)
                        st.success("Account created! Please sign in")
                        st.session_state.auth_mode = "Sign In"
                        st.rerun()
        
        st.markdown('</div></div>', unsafe_allow_html=True)

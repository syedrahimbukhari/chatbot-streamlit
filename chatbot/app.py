import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
api_key = os.getenv("Gimini_API_Key")
if not api_key:
    st.error("Please set the Gimini_API_Key environment variable in your .env file.")
    st.stop()

genai.configure(api_key=api_key)

available_models = [
    "gemini-1.5-flash-latest",
    "gemini-1.5-pro-latest"
]

st.set_page_config(page_title="AI ChatBox", page_icon=None, layout="wide")

st.sidebar.title("Settings")
model_name = st.sidebar.selectbox("Select Model", available_models)
model = genai.GenerativeModel(model_name)

if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}
    st.session_state.current_chat = None
    st.session_state.new_chat_mode = False
    st.session_state.new_chat_name = ""
    st.session_state.chat = None

def save_chat():
    if st.session_state.current_chat:
        st.session_state.chat_sessions[st.session_state.current_chat] = st.session_state.chat.history

def start_new_chat(chat_name):
    st.session_state.current_chat = chat_name
    if chat_name not in st.session_state.chat_sessions:
        st.session_state.chat_sessions[chat_name] = []
    st.session_state.chat = model.start_chat(history=st.session_state.chat_sessions[chat_name])
    st.rerun()

if st.sidebar.button("New Chat"):
    st.session_state.new_chat_mode = True
    st.session_state.new_chat_name = ""

if st.session_state.new_chat_mode:
    new_chat_name = st.sidebar.text_input("Enter Chat Name", st.session_state.new_chat_name, key="chat_name_input")
    if new_chat_name:
        if new_chat_name not in st.session_state.chat_sessions:
            start_new_chat(new_chat_name)
        st.session_state.new_chat_mode = False
        st.rerun()

chat_options = list(st.session_state.chat_sessions.keys())
if chat_options:
    selected_chat = st.sidebar.radio("Select Chat Session", chat_options, index=chat_options.index(st.session_state.current_chat) if st.session_state.current_chat in chat_options else 0)
    if selected_chat != st.session_state.current_chat:
        start_new_chat(selected_chat)

st.title("AI ChatBox")
st.write("Ask me anything!")

if st.session_state.chat:
    for message in st.session_state.chat.history:
        with st.chat_message("assistant" if message.role == "model" else message.role):
            st.markdown(message.parts[0].text)

user_input = st.chat_input("Type your message...", key="chat_input_focus")
if user_input:
    st.chat_message("user").markdown(user_input)
    response = st.session_state.chat.send_message(user_input)
    with st.chat_message("assistant"):
        st.markdown(response.text)
    
    save_chat()
    st.rerun()

if st.sidebar.button("Clear Chat History"):
    if st.session_state.current_chat in st.session_state.chat_sessions:
        del st.session_state.chat_sessions[st.session_state.current_chat]
        st.session_state.current_chat = None
        st.session_state.chat = None
    st.rerun()

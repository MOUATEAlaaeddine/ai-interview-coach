import streamlit as st
from openai import OpenAI
from streamlit_js_eval import streamlit_js_eval

st.set_page_config(page_title="AI Chatbot", page_icon="🤖")
st.title("🤖 AI Chatbot with OpenAI and Streamlit")

client = OpenAI(api_key=st.secrets["openai_api_key"])

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4o"
    
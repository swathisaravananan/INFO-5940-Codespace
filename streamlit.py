import os
import streamlit as st
from openai import OpenAI

# Initialize OpenAI client with API key from environment
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Try to detect an available model
def get_available_model():
    preferred_models = ["gpt-4o", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"]
    available = [m.id for m in client.models.list().data]

    for model in preferred_models:
        if model in available:
            return model
    # Fallback: just pick the first one you have
    return available[0]

MODEL_NAME = get_available_model()

# Streamlit UI
st.set_page_config(page_title="INFO-5940 Chatbot", layout="centered")
st.title(f"🤖 INFO-5940 Chatbot (using {MODEL_NAME})")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi! How can I help you today?"}]

# Show history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Chat input
if prompt := st.chat_input("Type your message..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Assistant reply
    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model=MODEL_NAME,
            messages=st.session_state.messages,
            stream=True
        )
        response = st.write_stream(stream)

    st.session_state.messages.append({"role": "assistant", "content": response})

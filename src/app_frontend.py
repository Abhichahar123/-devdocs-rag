import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/query"

st.set_page_config(page_title="DevDocs-RAG", page_icon="💬")

st.title("DevDocs-RAG")
st.caption("Ask anything about Razorpay's API documentation")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["text"])
        if msg.get("sources"):
            st.caption("Sources: " + ", ".join(msg["sources"]))

question = st.chat_input("Ask a question...")

if question:
    st.session_state.messages.append({"role": "user", "text": question})
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(API_URL, json={"question": question})
                data = response.json()
                answer = data["answer"]
                sources = data["sources"]
            except Exception as e:
                answer = f"Error: could not reach the server. ({e})"
                sources = []

            st.write(answer)
            if sources:
                st.caption("Sources: " + ", ".join(sources))

    st.session_state.messages.append({
        "role": "assistant",
        "text": answer,
        "sources": sources,
    })
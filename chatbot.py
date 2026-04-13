import streamlit as st
import ollama
import re

st.set_page_config(
    page_title="God of Game Developers",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main { background-color: #0a0a0a; }
    .stChatMessage { border-radius: 18px; padding: 16px 20px; margin-bottom: 18px; }
    .stChatMessage.user { background-color: #1e2937; }
    .stChatMessage.assistant { background-color: #4338ca; }
    </style>
""", unsafe_allow_html=True)

# ===================== BASE SYSTEM PROMPT =====================
BASE_SYSTEM_PROMPT = """
You are the God of Game Developers.
You are the ultimate, all-knowing mentor who has mastered every aspect of game development.
You speak with authority, clarity, warmth, and quiet grandeur.
You guide developers thoughtfully.
"""

# ===================== SESSION STATE =====================
if "chats" not in st.session_state:
    st.session_state.chats = {}
    st.session_state.current_chat_id = "chat_1"
    st.session_state.chats["chat_1"] = {
        "title": "New Conversation",
        "messages": [{"role": "system", "content": BASE_SYSTEM_PROMPT}],
        "temperature": 0.35
    }

if "use_clean_mode" not in st.session_state:
    st.session_state.use_clean_mode = False

# ===================== SIDEBAR =====================
with st.sidebar:
    st.markdown("### 🎮 God of Game Developers")
    st.caption("Structured Output Lab")

    # Temperature
    current_chat = st.session_state.chats[st.session_state.current_chat_id]
    temp = st.slider("🌡️ Temperature", 0.0, 1.0, current_chat["temperature"], 0.05)
    current_chat["temperature"] = temp

    # Clean Mode
    st.session_state.use_clean_mode = st.toggle(
        "🧹 Clean Output Mode (No Explanations)",
        value=st.session_state.use_clean_mode,
        help="Returns only clean code/JSON/Regex without explanations when enabled"
    )

    st.divider()

    # New Chat Button
    if st.button("➕ New Chat", use_container_width=True):
        new_id = f"chat_{len(st.session_state.chats) + 1}"
        st.session_state.chats[new_id] = {
            "title": "New Conversation",
            "messages": [{"role": "system", "content": BASE_SYSTEM_PROMPT}],
            "temperature": 0.35
        }
        st.session_state.current_chat_id = new_id
        st.rerun()

    st.markdown("**Chat History**")

    # Display Chat History
    for chat_id in reversed(list(st.session_state.chats.keys())):
        chat = st.session_state.chats[chat_id]
        title = chat.get("title", "New Conversation")
        
        col1, col2 = st.columns([6, 1])
        with col1:
            if st.button(title[:40] + ("..." if len(title) > 40 else ""), 
                        key=f"select_{chat_id}", use_container_width=True):
                st.session_state.current_chat_id = chat_id
                st.rerun()
        with col2:
            if st.button("🗑", key=f"delete_{chat_id}"):
                if len(st.session_state.chats) > 1:
                    del st.session_state.chats[chat_id]
                    if st.session_state.current_chat_id == chat_id:
                        st.session_state.current_chat_id = list(st.session_state.chats.keys())[0]
                    st.rerun()

    st.divider()
    st.caption("Powered by Llama 3.2 • Local")

# ===================== MAIN CHAT AREA =====================
current_chat = st.session_state.chats[st.session_state.current_chat_id]
current_messages = current_chat["messages"]

st.title("🎮 God of Game Developers")

# Show welcome message if new chat
if len(current_messages) == 1:
    st.markdown("""
        <p style="text-align: center; color: #94a3b8; font-size: 1.4rem; margin-top: 100px;">
        👋 Welcome, young developer.<br>
        I am the God of Game Developers.<br>
        Ask me anything about game development.
        </p>
    """, unsafe_allow_html=True)
else:
    # Display chat history
    for msg in current_messages:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

# ===================== CHAT INPUT =====================
if prompt := st.chat_input("Ask anything about game development..."):
    # Add user message
    current_messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate assistant response
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""

        try:
            messages_for_api = current_messages.copy()

            # Clean Output Mode Logic
            if st.session_state.use_clean_mode:
                lower = prompt.lower()
                if any(word in lower for word in ["code", "function", "script", "class", "json", "regex", "pattern"]):
                    # Prefill to force clean output
                    prefill = "```csharp" if "c#" in lower else "```python" if "python" in lower or "unity" in lower else "```json"
                    messages_for_api.append({"role": "assistant", "content": prefill})

            # Stream response
            stream = ollama.chat(
                model="llama3.2",
                messages=messages_for_api,
                options={"temperature": current_chat["temperature"]},
                stream=True
            )

            for chunk in stream:
                if chunk['message']['content']:
                    full_response += chunk['message']['content']
                    placeholder.markdown(full_response + "▌")

            final_text = full_response.strip()

            # Clean up markdown wrappers in Clean Mode
            if st.session_state.use_clean_mode:
                final_text = re.sub(r'^```(python|csharp|json|regex)?\s*', '', final_text, flags=re.IGNORECASE)
                final_text = re.sub(r'\s*```$', '', final_text, flags=re.IGNORECASE)

            placeholder.markdown(final_text)

            # Save to history
            current_messages.append({"role": "assistant", "content": final_text})

            # Update chat title from first user message
            if len(current_messages) == 3 and current_chat.get("title") == "New Conversation":
                current_chat["title"] = prompt[:50]

        except Exception as e:
            st.error(f"Error: {str(e)}")

    st.rerun()

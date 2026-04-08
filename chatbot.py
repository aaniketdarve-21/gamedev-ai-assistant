import streamlit as st
import ollama

# Page configuration
st.set_page_config(
    page_title="GameDev AI Assistant",
    page_icon="🎮",
    layout="centered"
)

# Custom CSS for better look
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stChatMessage {
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Title and description
st.title("🎮 GameDev AI Assistant")
st.markdown("**Your personal AI Game Design & Development Mentor** powered by Llama 3.2")

st.caption("Ask anything about Unity, Unreal Engine, Game Design, Mechanics, AI, Monetization, etc.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask me about game development..."):
    
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking like a Senior Game Designer..."):
            try:
                response = ollama.chat(
                    model="llama3.2",
                    messages=st.session_state.messages
                )
                answer = response['message']['content']
                
                st.markdown(answer)
                
                # Save to history
                st.session_state.messages.append({"role": "assistant", "content": answer})
                
            except Exception as e:
                st.error(f"Something went wrong: {str(e)}")
import streamlit as st
import time
import uuid
import pandas as pd
from assistant import get_answer
from db import save_conversation, save_feedback, get_recent_conversations, get_feedback_stats


def print_log(message):
    print(message, flush=True)

print_log("Streamlit app loop completed")

def init_project():
    st.write("Before starting the app please select your Time zone")
    df = pd.read_csv('../data/time_zone.csv')

    tz_zone = pd.Series(df['timezone']).unique().tolist()

def main():

    """
     A conversation with a session id which here we call it a conversation id. 
     During this conversation, user can ask several question or the same question but with different
     parameters. A conversation id is defined by the session id. But each Question/answer is stored with it's own id.
    """
    print_log("Starting the Course Assistant application")
    st.title("Recipe Assistant")

    # Session state initialization
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
        print_log(f"New session started with ID: {st.session_state.session_id}")
    if 'count' not in st.session_state:
        st.session_state.count = 0
        print_log("Feedback count initialized to 0")
    if 'conversation_id' not in st.session_state:
        # Conversation state initialization
        st.session_state.conversation_id = None

if __name__ == "__main__":
    print_log("Recipe Assistant application started")
    main()

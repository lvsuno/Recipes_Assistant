from prompt_builder import WELCOME_MSG
import streamlit as st
import time
import uuid
import pandas as pd
from assistant import get_answer
from db import TZ_ZONE, save_conversation, save_feedback, get_recent_conversations, get_feedback_stats
import os
from app_utils.ui import (create_button, 
    create_chat_msg,
    create_welcome_msg,
    disclaimer_dialog,
    menu_ui
)


APP_NAME='NOUDOUDOU'

APP_DESC_TEXT: str = """
"NOUDOUDOU" is your personal recipe helper.\n
This is an AI-powered digital assistant based on more\n 
than 15 000 recipes from [epicurious.com](https://www.epicurious.com/).\n
You can get some advices based on your ingredients or\n
ask about a specific recipe.
"""

st.set_page_config(page_title=APP_NAME, page_icon="👩‍🍳", layout="wide")

def print_log(message):
    print(message, flush=True)





def init_project():
    """
    Iniatilize the project by choosing a time zone
    """
    # st.write("Before starting the app please login first")
    
    

    # df = pd.read_csv('data/time_zone.csv')

    # tz_zone = pd.Series(df['timezone']).unique().tolist()
    # # tz_zone.insert(0, "") # add 1st blank entry so that 1st option does not get auto selected
    # chosen_tz_zone = st.selectbox("Select your time zone", tz_zone, 
    #                               index=tz_zone.index("Canada/Eastern"))
    # if chosen_tz_zone != "":
    #     # txt = f"You chose {chosen_tz_zone}"
    #     # st.write(f":green[{txt}]")
    #     os.environ['TZ_ZONE'] = chosen_tz_zone

def main():

    """
     A conversation with a session id which here we call it a conversation id. 
     During this conversation, user can ask several question or the same question but with different
     parameters. A conversation id is defined by the session id. But each Question/answer is stored with it's own id.
    """

    model_choice, register_button, login_button = menu_ui(APP_DESC_TEXT)

    user_name = 'guest'
    print_log("Starting the Course Assistant application")
    st.title("Recipe Assistant")
    
    # init_project()
    if 'first_run' not in st.session_state:
        st.session_state.first_run = True
        disclaimer_dialog()   

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

    with st.sidebar:
        # Create New_chat button
        _, _, new_chat_col2 = st.columns([1, 1, 1])

        
        with new_chat_col2:
            new_chat_button = create_button(
                "new_chat",
                ":pencil:",
                default=False,
                help="New Chat",
            )
        
        show_history_on = st.toggle("Show History")


# ========= Chat box =======
    new_chat: bool = not st.session_state.messages 

    if new_chat:
        st.session_state.messages = []
        # Create first message
        create_welcome_msg(
            msg=WELCOME_MSG.format(user_name=user_name, app_name=APP_NAME)
        )







if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("How to cook rice?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})



print_log("Streamlit app loop completed")

if __name__ == "__main__":
    print_log("Recipe Assistant application started")
    main()

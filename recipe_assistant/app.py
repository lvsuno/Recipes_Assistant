"""
Main file for the streamlit app
"""

import uuid
from typing import Any

import pandas as pd
import streamlit as st
from db import (
    check_user,
    create_chat,
    create_user,
    save_feedback,
    create_session,
    get_recent_chats,
    save_conversation,
    get_feedback_stats,
)
from assistant import get_answer
from ui import (
    menu_ui,
    stream_text,
    create_chat_msg,
    disclaimer_dialog,
    create_welcome_msg,
    show_current_chat_history,
    build_chat_history_ui,
)
from prompt_builder import WELCOME_MSG
from app_utils.utils import BOT_AVATAR_FILE, USER_AVATAR_FILE, session_keys

APP_NAME = 'NOUDOUDOU'

APP_DESC_TEXT: str = """
"NOUDOUDOU" is your personal recipe helper.\n
This is an AI-powered digital assistant based on more\n
than 13 000 recipes from [epicurious.com](https://www.epicurious.com/).\n
You can get some advices based on your ingredients or\n
ask about a specific recipe.
"""
AVATARS: dict[str, Any] = {
    "assistant": str(BOT_AVATAR_FILE),
    "user": str(USER_AVATAR_FILE),
}
st.set_page_config(page_title=APP_NAME, page_icon="👩‍🍳", layout="wide")


def print_log(message):
    """
    Print message in the console
    """
    print(message, flush=True)


def init_project():
    """
    Iniatilize the project by choosing a time zone
    """
    # st.write("Before starting the app please login first")

    if 'first_run' not in st.session_state:
        st.session_state.first_run = True
        disclaimer_dialog()
    else:
        st.session_state.first_run = False

    # Session state initialization
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
        print_log(f"New session started with ID: {st.session_state.session_id}")

    if 'user_login_state' not in st.session_state:
        st.session_state["user_login_state"] = False
    # if 'user_name' not in st.session_state:
    #     st.session_state["user_login_state"] = False
    else:
        st.session_state["user_login_state"] = True

    session_keys('user_name', None)
    session_keys('key_val', None)
    session_keys('messages', [])
    session_keys('fbk_sel', False)
    session_keys('new_llm_answer', False)
    session_keys("h_tog", False)
    session_keys("ui_h01", False)
    session_keys("ui_h02", False)
    session_keys("ui_h03", False)
    session_keys("ui_h04", False)
    session_keys("ui_h05", False)
    # df = pd.read_csv('data/time_zone.csv')

    # tz_zone = pd.Series(df['timezone']).unique().tolist()
    # # tz_zone.insert(0, "") # add 1st blank entry so that 1st option does not get auto selected
    # chosen_tz_zone = st.selectbox("Select your time zone", tz_zone,
    #                               index=tz_zone.index("Canada/Eastern"))
    # if chosen_tz_zone != "":
    #     # txt = f"You chose {chosen_tz_zone}"
    #     # st.write(f":green[{txt}]")
    #     os.environ['TZ_ZONE'] = chosen_tz_zone


def feedback_callback():
    st.session_state.fbk_sel = True
    if st.session_state.fbk is not None:
        save_feedback(st.session_state.conv_id, st.session_state.fbk)


def main():
    """
    A conversation with a session id which here we call it a conversation id.
    During this conversation, user can ask several question or the same question but with different
    parameters. A conversation id is defined by the session id.
    But each Question/answer is stored with it's own id.
    """

    init_project()

    model_choice, user_name = menu_ui(APP_DESC_TEXT)
    if user_name:
        st.session_state["user_name"] = user_name
        if check_user(user_name):
            create_session(st.session_state.session_id, user_name)

        else:
            create_user(user_name)
            create_session(st.session_state.session_id, user_name)

    # if model_choice != " ":
    #     check_validity = check_llm_api_key(model_choice)
    # st.write(st.session_state["key_val"])

    if st.session_state["user_name"] and model_choice != " ":

        print_log("Starting the Course Assistant application")
        st.title("Recipe Assistant")

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
                # session_keys('new_chat', False)
                new_chat_button = st.button(
                    key="new_chat",
                    label=":pencil: new chat",
                    help="New Chat",
                    # on_click=,
                )
                if new_chat_button:
                    st.session_state["messages"].clear()
                    st.session_state.chat_id = 'ch_' + str(uuid.uuid4())
                    create_chat(st.session_state.chat_id, st.session_state.session_id)
                    st.session_state.new_llm_answer = False
                    st.session_state.fbk_sel = False
                    st.session_state["ui_h01"] = False
                    st.session_state["ui_h02"] = False
                    st.session_state["ui_h03"] = False
                    st.session_state["ui_h04"] = False
                    st.session_state["ui_h05"] = False

            show_history_on = st.toggle("Show History", key='h_tog')
            if show_history_on:
                recent_chats = get_recent_chats(st.session_state["user_name"])
                build_chat_history_ui(recent_chats, AVATARS)

            #     st.session_state.new_llm_answer = False
            #     st.session_state.fbk = False

    if st.session_state["key_val"] and model_choice != " ":
        # ========= Chat box =======
        new_chat: bool = not st.session_state.messages

        if new_chat:
            st.session_state.messages = []
            if 'chat_id' not in st.session_state:
                st.session_state.chat_id = 'ch_' + str(uuid.uuid4())
                # Create a chat in the database
                create_chat(st.session_state.chat_id, st.session_state.session_id)
            # Create first message
            create_welcome_msg(
                msg=WELCOME_MSG.format(
                    user_name=st.session_state["user_name"], app_name=APP_NAME
                )
            )
        else:
            # show chat message history
            show_current_chat_history(avatars=AVATARS)

        # for message in st.session_state.messages:
        #     with st.chat_message(message["role"]):
        #         st.markdown(message["content"])

        if prompt := st.chat_input("How to cook rice?"):
            st.session_state.new_llm_answer = False
            st.session_state.fbk_sel = False
            st.session_state.conv_save_status = 0

            create_chat_msg(
                content=stream_text(prompt, sleep=0.001),
                role="user",
                avatar=AVATARS["user"],
            )
            if 'conv_id' not in st.session_state:
                st.session_state.conv_id = 'cv_' + str(uuid.uuid4())
            else:
                st.session_state.update({"conv_id": 'cv_' + str(uuid.uuid4())})
            with st.chat_message("assistant", avatar=AVATARS["assistant"]):
                with st.spinner("One moment..."):
                    raw_answer = get_answer(
                        prompt, model_choice, st.session_state.messages
                    )
                    st.write_stream(stream_text(raw_answer["answer"], sleep=0.01))
            save_conversation(
                st.session_state.conv_id, st.session_state.chat_id, prompt, raw_answer
            )
            st.session_state.new_llm_answer = True
            st.session_state.messages.append(
                {"role": "assistant", "content": raw_answer["answer"]}
            )
    elif not st.session_state["key_val"] and model_choice != " ":
        st.error('Your API Key is invalid', icon="🚨")
    if (
        st.session_state.new_llm_answer
        or st.session_state.ui_h01
        or st.session_state.ui_h02
        or st.session_state.ui_h03
        or st.session_state.ui_h04
        or st.session_state.ui_h05
    ):
        st.markdown("### Rate this answer:")
        st.feedback(
            "stars",
            key='fbk',
            on_change=feedback_callback,
            disabled=st.session_state["fbk_sel"],
        )
        # if isinstance(fbk_sel, int) and fbk_sel:
        #     print_log(st.session_state.conv_save_status)
        #     if st.session_state["conv_save_status"] == 0:
        #         st.session_state["conv_save_status"] = 1
        #         save_feedback(st.session_state.conv_id, fbk_sel)

    print_log("Streamlit app loop completed")


if __name__ == "__main__":
    print_log("Recipe Assistant application started")
    main()

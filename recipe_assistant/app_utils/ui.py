from collections.abc import Iterable
from typing import Any

import streamlit as st
from .utils import (session_keys, 
                    is_valid_email,
                    stream_text,
                    BOT_DISCLAIMER_FILE,
                    BOT_AVATAR_FILE
)



def show_md_file(path, **kwargs):
    """
    Show Markdown content that are present in a file.
    If you have some variables, you can pass it through kwargs.
    """
    with open(path, encoding="utf-8") as f:
        content = f.read()
    if kwargs:
        st.markdown(content.format(**kwargs))
    else:
        st.markdown(content)


def create_button(state_key: str, label: str, default: bool = False, **kwargs) -> bool:
    session_keys(state_key, default)

    def click_button():
        st.session_state[state_key] = True

    st.button(label=label, key=f"ui_{state_key}", on_click=click_button, **kwargs)

    return st.session_state[state_key]


def create_chat_msg(
    content: str | Iterable[str],
    role: str,
    avatar: Any = None,
    state_key: str = "messages",
):
    full_content: str
    with st.chat_message(name=role, avatar=avatar):
        full_content = st.write_stream(content)  # type: ignore

    # Add assistant response to chat history
    st.session_state[state_key].append({"role": role, "content": full_content})


def create_welcome_msg(msg: str):
    """
    show the welcome message
    """
    create_chat_msg(content=stream_text(msg, sleep=0.1), 
                    role="assistant", avatar=str(BOT_AVATAR_FILE))


def show_chat_history(avatars: dict[str, Any], state_key: str = "messages"):
    # show chat message history
    for msg_dict in st.session_state[state_key]:
        role: str = msg_dict["role"]
        with st.chat_message(name=role, avatar=avatars[role]):
            st.markdown(msg_dict["content"])


def menu_ui(app_desc_text):
    model_col, _, _, _, _, login_col, register_col, about_col = st.columns([1.7,1,1,1,1,1,1,1], gap="small")
    
    with model_col:
        model_choice = st.selectbox(
        "Select a model:",
        ["Groq","ollama/phi3", "openai/gpt-3.5-turbo", "openai/gpt-4o", "openai/gpt-4o-mini"]
        )
    
    with register_col:
        with st.popover(":material/Person: register"):
            with st.form(key="register_form", border=False):
                st.text_input(
                    "Enter your pseudo",
                    "jensen",
                    key="register_pseudo",
                )
                st.text_input(
                    "Enter your email",
                    "jensen@gmail.com",
                    key="register_email",
                )
                register_button = st.form_submit_button(label="register")

    
    with login_col:
        with st.popover(":material/Login: login"):
            with st.form(key="login_form", border=False):
                st.text_input(
                    "Enter your pseudo",
                    "jensen",
                    key="login_pseudo",
                )
                st.text_input(
                    "Enter your email",
                    "jensen@gmail.com",
                    key="login_email",
                )
                login_button = st.form_submit_button(label="login")

    with about_col:
        with st.popover(":material/Info: :red[**About**]"):
            st.info(app_desc_text, icon="💡")

    return model_choice, register_button, login_button

@st.dialog("Disclaimer")
def disclaimer_dialog():
    """
    Use this dialog at the begining 
    """
    show_md_file(BOT_DISCLAIMER_FILE)


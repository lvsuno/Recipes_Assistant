from typing import Any
from collections.abc import Iterable

import groq
import openai
import streamlit as st

from .cst import GROQ_API_KEY, OPENAI_API_KEY
from .utils import (
    BOT_AVATAR_FILE,
    BOT_DISCLAIMER_FILE,
    stream_text,
    session_keys
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
    """
    Function to create a button
    """
    session_keys(state_key, default)

    def click_button():
        st.session_state[state_key] = True

    st.button(label=label, key=f"ui_{state_key}", on_click=click_button, **kwargs)

    return st.session_state[state_key]


def menu_ui(app_desc_text: str):
    """
    Create Menu
    """
    model_col, _, _, _, _, login_col, about_col = st.columns(
        [1.7, 1, 1, 1, 1, 1, 1], gap="small"
    )

    user_name = None

    with model_col:
        model_choice = st.selectbox(
            "**Select a model**:",
            [
                " ",
                "Groq/gemma2-9b-it",
                "Groq/llama-3.1-70b-versatile",
                "Groq/mixtral-8x7b-32768",
                "ollama/phi3",
                "openai/gpt-3.5-turbo",
                "openai/gpt-4o",
                "openai/gpt-4o-mini",
            ],
            disabled=not st.session_state["user_login_state"],
            key='model_choice_box',
            on_change=check_llm_api_key,
        )

    # with register_col:
    #     with st.popover(":material/Person: register"):
    #         with st.form(key="register_form", border=False):
    #             st.text_input(
    #                 "Enter your pseudo",
    #                 "jensen",
    #                 key="register_pseudo",
    #             )
    #             # st.text_input(
    #             #     "Enter your email",
    #             #     "jensen@gmail.com",
    #             #     key="register_email",
    #             # )
    #             register_button = st.form_submit_button(label="register")

    with login_col:
        with st.popover(
            "login",
            icon=":material/login:",
            disabled=st.session_state["user_login_state"],
        ):
            with st.form(key="login_form", border=False):
                pseudo_val = st.text_input(
                    "Enter your pseudo",
                    "jensen",
                    key="login_pseudo",
                )
                # st.text_input(
                #     "Enter your email",
                #     "jensen@gmail.com",
                #     key="login_email",
                # )
                login_button = st.form_submit_button(
                    label="login",
                    on_click=session_keys("user_login_state", True),
                    disabled=st.session_state["user_login_state"],
                )

            if login_button:
                user_name = pseudo_val
                # st.session_state["user_login_state"] = True

    with about_col:
        with st.popover(":red[**About**]", icon=":material/info:"):
            st.info(app_desc_text, icon="💡")

    return model_choice, user_name


@st.dialog("Disclaimer")
def disclaimer_dialog():
    """
    Use this dialog at the begining
    """
    show_md_file(BOT_DISCLAIMER_FILE)


def check_llm_api_key() -> None:
    """
    Check validity of the api key
    """
    model_choice = st.session_state.model_choice_box
    if model_choice.startswith('openai/'):
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        try:
            client.models.list()
        except openai.AuthenticationError:
            st.session_state["key_val"] = False

        else:
            st.session_state["key_val"] = True
    elif model_choice.startswith('Groq/'):
        client = groq.Groq(api_key=GROQ_API_KEY)
        try:
            client.models.list()
        except groq.AuthenticationError:
            st.session_state["key_val"] = False
        else:
            st.session_state["key_val"] = True
    else:
        st.session_state["key_val"] = True


def create_chat_msg(
    content: str | Iterable[str],
    role: str,
    avatar: Any = None,
    state_key: str = "messages",
):
    """
    Create chat message
    """
    full_content: str
    with st.chat_message(name=role, avatar=avatar):
        full_content = st.write_stream(content)  # type: ignore

    # Add assistant response to chat history
    st.session_state[state_key].append({"role": role, "content": full_content})


def create_welcome_msg(msg: str):
    """
    show the welcome message
    """
    create_chat_msg(
        content=stream_text(msg, sleep=0.05),
        role="assistant",
        avatar=str(BOT_AVATAR_FILE),
    )


def show_current_chat_history(avatars: dict[str, Any], state_key: str = "messages"):
    # show chat message history
    for msg_dict in st.session_state[state_key]:
        role: str = msg_dict["role"]
        with st.chat_message(name=role, avatar=avatars[role]):
            st.markdown(msg_dict["content"])


# def show_assistant_response(Iterable[str])

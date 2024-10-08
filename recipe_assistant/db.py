"""
Setting the operations needed to connect and interact with the database
"""

import os
from datetime import datetime
from zoneinfo import ZoneInfo

import psycopg2
from psycopg2.extras import DictCursor

# from dotenv import load_dotenv

# load_dotenv()
TZ_ZONE = os.getenv('TZ_ZONE')
# print(TZ_ZONE, flush=True)
tz = ZoneInfo(TZ_ZONE)

DEPLOY = os.getenv('DEPLOY', 'local')


def get_db_connection():
    if DEPLOY == 'local':
        return psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "postgres"),
            database=os.getenv("POSTGRES_DB", "course_assistant"),
            user=os.getenv("POSTGRES_USER", "your_username"),
            password=os.getenv("POSTGRES_PASSWORD", "your_password"),
        )
    elif DEPLOY == 'cloud-streamlit':
        import sqlite3

        return sqlite3.connect("Rag.db")


def init_db():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS Users")
            cur.execute("DROP TABLE IF EXISTS Sessions")
            cur.execute("DROP TABLE IF EXISTS Chats")
            cur.execute("DROP TABLE IF EXISTS Conversations CASCADE")
            cur.execute("DROP TABLE IF EXISTS Feedbacks")

            cur.execute(
                """
                CREATE TABLE Users (
                    id SERIAL PRIMARY KEY,
                    pseudo TEXT NOT NULL,
                    creation_time TIMESTAMP WITH TIME ZONE NOT NULL
                )
            """
            )

            cur.execute(
                """
                CREATE TABLE Sessions (
                    id TEXT PRIMARY KEY,
                    user_id INTEGER REFERENCES Users(id),
                    session_time TIMESTAMP WITH TIME ZONE NOT NULL
                )
            """
            )

            cur.execute(
                """
                CREATE TABLE Chats (
                    id TEXT PRIMARY KEY,
                    session_id TEXT REFERENCES Sessions(id),
                    chat_time TIMESTAMP WITH TIME ZONE NOT NULL
                )
            """
            )

            cur.execute(
                """
                CREATE TABLE Conversations (
                    id TEXT PRIMARY KEY,
                    chat_id TEXT REFERENCES Chats(id),
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    model_used TEXT NOT NULL,
                    response_time FLOAT NOT NULL,
                    relevance TEXT NOT NULL,
                    relevance_explanation TEXT NOT NULL,
                    prompt_tokens INTEGER NOT NULL,
                    completion_tokens INTEGER NOT NULL,
                    total_tokens INTEGER NOT NULL,
                    eval_prompt_tokens INTEGER NOT NULL,
                    eval_completion_tokens INTEGER NOT NULL,
                    eval_total_tokens INTEGER NOT NULL,
                    openai_cost FLOAT NOT NULL,
                    timestamp TIMESTAMP WITH TIME ZONE NOT NULL
                )
            """
            )

            cur.execute(
                """
                CREATE TABLE Feedbacks (
                    id SERIAL PRIMARY KEY,
                    conversation_id TEXT REFERENCES Conversations(id),
                    CONSTRAINT conversations_id UNIQUE (conversation_id),
                    feedback INTEGER NOT NULL,
                    timestamp TIMESTAMP WITH TIME ZONE NOT NULL
                )
            """
            )
            # email TEXT NOT NULL,
        conn.commit()
    finally:
        conn.close()


def create_user(pseudo: str, timestamp=None):
    """
    Create chat into the database.

    A chat has an unique id is associated with one
    session and can have many conversations
    """
    if timestamp is None:
        timestamp = datetime.now(tz)

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO Users (pseudo, creation_time) VALUES (%s, COALESCE(%s, CURRENT_TIMESTAMP))
            """,
                (pseudo, timestamp),
            )
        conn.commit()
    finally:
        conn.close()


def check_user(pseudo: str) -> bool:
    """
    Check if the user exists
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            query = "SELECT EXISTS(SELECT 1 FROM Users WHERE pseudo = %s);"
            value_to_check = (pseudo,)
            cur.execute(query, value_to_check)
            exists = cur.fetchone()[0]
        return exists
    finally:
        conn.close()


def get_user_id(pseudo: str):
    """Get user id"""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(
                f"""
                SELECT id FROM Users where pseudo='{pseudo}'
            """
            )
            return cur.fetchone()
    finally:
        conn.close()


def create_session(session_id: str, pseudo: str, timestamp=None):
    """
    Create chat into the database.

    A chat has an unique id is associated with one
    session and can have many conversations
    """
    if timestamp is None:
        timestamp = datetime.now(tz)
    user_id = get_user_id(pseudo)[0]
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO Sessions (id, user_id, session_time) VALUES (%s, %s, COALESCE(%s, CURRENT_TIMESTAMP))
            """,
                (session_id, user_id, timestamp),
            )
        conn.commit()
    finally:
        conn.close()


def create_chat(chat_id: str, session_id: str, timestamp=None):
    """
    Create chat into the database.

    A chat has an unique id is associated with one
    session and can have many conversations
    """
    if timestamp is None:
        timestamp = datetime.now(tz)

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO Chats (id, session_id, chat_time) VALUES (%s, %s, COALESCE(%s, CURRENT_TIMESTAMP))
            """,
                (chat_id, session_id, timestamp),
            )
        conn.commit()
    finally:
        conn.close()


def save_conversation(id, chat_id, question, answer_data, timestamp=None):
    if timestamp is None:
        timestamp = datetime.now(tz)

    conn = get_db_connection()
    # id = f"{session_id}_{timestamp.strftime('%m/%d/%Y %H:%M:%S')}"
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO Conversations
                (id, chat_id, question, answer, model_used, response_time, relevance,
                relevance_explanation, prompt_tokens, completion_tokens, total_tokens,
                eval_prompt_tokens, eval_completion_tokens, eval_total_tokens, openai_cost, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, COALESCE(%s, CURRENT_TIMESTAMP))
            """,
                (
                    id,
                    chat_id,
                    question,
                    answer_data["answer"],
                    answer_data["model_used"],
                    answer_data["response_time"],
                    answer_data["relevance"],
                    answer_data["relevance_explanation"],
                    answer_data["prompt_tokens"],
                    answer_data["completion_tokens"],
                    answer_data["total_tokens"],
                    answer_data["eval_prompt_tokens"],
                    answer_data["eval_completion_tokens"],
                    answer_data["eval_total_tokens"],
                    answer_data["openai_cost"],
                    timestamp,
                ),
            )
        conn.commit()
    finally:
        conn.close()


#    return id


def save_feedback(conversation_id, feedback, timestamp=None):
    """
    Save Feedback to the database
    """
    if timestamp is None:
        timestamp = datetime.now(tz)

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO Feedbacks (conversation_id, feedback, timestamp) VALUES (%s, %s, COALESCE(%s, CURRENT_TIMESTAMP))",
                (conversation_id, feedback, timestamp),
            )
        conn.commit()
    finally:
        conn.close()


def get_recent_chats(pseudo, limit=5):
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            query = f"""
                WITH user_sessions AS (
                SELECT s.id
                FROM Users u
                LEFT JOIN Sessions s ON u.id = s.user_id
                WHERE u.pseudo='{pseudo}'
                ),
                user_chats AS (
                SELECT c.id
                FROM Chats c
                WHERE c.session_id IN (SELECT id FROM user_sessions)
                ),
                subq AS (
                SELECT chat_id, question, timestamp,
                rank() OVER (PARTITION BY chat_id ORDER BY timestamp ASC) AS rk
                FROM Conversations WHERE chat_id IN (SELECT id FROM user_chats)
                )
                SELECT c.question, c.chat_id, h.chat_time
                FROM subq c
                LEFT JOIN Chats h ON h.id = c.chat_id
                WHERE c.rk=1
            """
            query += "ORDER BY h.chat_time DESC LIMIT %s"
            cur.execute(query, (limit,))
            return cur.fetchall()
    finally:
        conn.close()


def get_a_chat(chat_id: str):
    """
    Get a specific chat given a chat_id.
    Remember that a chat is composed of several conversations
    """
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            query = f"""
                SELECT question, answer
                FROM Conversations
                WHERE chat_id = '{chat_id}'
                ORDER BY timestamp ASC
            """

            cur.execute(query)
            return cur.fetchall()
    finally:
        conn.close()


def get_feedback_stats():
    """
    Get feedback stats
    """
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(
                """
                SELECT
                    SUM(CASE WHEN feedback > 0 THEN 1 ELSE 0 END) as thumbs_up,
                    SUM(CASE WHEN feedback < 0 THEN 1 ELSE 0 END) as thumbs_down
                FROM Feedbacks
            """
            )
            return cur.fetchone()
    finally:
        conn.close()

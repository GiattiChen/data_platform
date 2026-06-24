"""用户登录认证（简化版）"""
import functools
import hashlib
import json
import time
import uuid
from datetime import datetime, timedelta
from pathlib import Path

import streamlit as st
from loguru import logger
from streamlit_extras.colored_header import colored_header
from streamlit_javascript import st_javascript

from utils.constant import (
    AUTH_TOKEN_KEY,
    CREDENTIAL_FILE_PATH,
    LOGIN_STATE_DIR,
    VERSION,
)

LOGIN_STATE_DIR.mkdir(exist_ok=True)


def init_session_state():
    defaults = {
        "logged_in": False,
        "username": None,
        "auth_token": None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def generate_auth_token(username: str) -> str:
    unique = f"{username}_{time.time()}_{uuid.uuid4()}"
    return hashlib.sha256(unique.encode()).hexdigest()


def save_login_state(username: str, token: str):
    state_file = LOGIN_STATE_DIR / f"{token[:16]}.json"
    state_data = {
        "username": username,
        "token": token,
        "login_time": datetime.now().isoformat(),
        "expire_time": (datetime.now() + timedelta(days=7)).isoformat(),
    }
    with open(state_file, "w") as f:
        json.dump(state_data, f)


def load_login_state(token: str) -> tuple[bool, dict | None]:
    if not token:
        return False, None
    state_file = LOGIN_STATE_DIR / f"{token[:16]}.json"
    if not state_file.exists():
        return False, None
    try:
        with open(state_file, "r") as f:
            state_data = json.load(f)
        if datetime.now() > datetime.fromisoformat(state_data["expire_time"]):
            state_file.unlink()
            return False, None
        if state_data.get("token") != token:
            return False, None
        return True, state_data
    except Exception as e:
        logger.error(f"加载登录状态失败: {e}")
        return False, None


def load_credentials() -> dict[str, str]:
    users = {}
    if not CREDENTIAL_FILE_PATH.exists():
        return users
    with open(CREDENTIAL_FILE_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                parts = line.split(None, 1)
                if len(parts) == 2:
                    users[parts[0]] = parts[1]
    return users


def get_token_from_local_storage() -> str | None:
    token = st_javascript(f"localStorage.getItem('{AUTH_TOKEN_KEY}');")
    time.sleep(0.3)
    if token and token != "null" and token.strip():
        return token
    return None


def save_token_to_local_storage(token: str):
    st_javascript(f"localStorage.setItem('{AUTH_TOKEN_KEY}', '{token}');")


def clear_token_from_local_storage():
    st_javascript(f"localStorage.removeItem('{AUTH_TOKEN_KEY}');")


def login():
    st.markdown(
        "<style>[data-testid='stSidebar'] { display: none; }</style>",
        unsafe_allow_html=True,
    )
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        colored_header(
            label="登录 Data Platform",
            description="数据管理系统",
            color_name="blue-70",
        )
        with st.form("login_form"):
            username = st.text_input("用户名", placeholder="请输入用户名")
            password = st.text_input("密码", type="password", placeholder="请输入密码")
            submit = st.form_submit_button("登录", type="primary", use_container_width=True)
            if submit:
                if not username or not password:
                    st.error("请输入用户名和密码")
                else:
                    users = load_credentials()
                    if username in users and users[username] == password:
                        token = generate_auth_token(username)
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.auth_token = token
                        save_login_state(username, token)
                        save_token_to_local_storage(token)
                        st.toast("登录成功", icon="🎊")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("用户名或密码错误")


def logout():
    clear_token_from_local_storage()
    if st.session_state.auth_token:
        state_file = LOGIN_STATE_DIR / f"{st.session_state.auth_token[:16]}.json"
        if state_file.exists():
            state_file.unlink()
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.auth_token = None
    time.sleep(0.5)
    st.rerun()


def check_login() -> bool:
    init_session_state()
    if st.session_state.logged_in and st.session_state.username:
        return True
    token = get_token_from_local_storage()
    is_valid, user_data = load_login_state(token)
    if is_valid:
        st.session_state.logged_in = True
        st.session_state.username = user_data["username"]
        st.session_state.auth_token = token
        return True
    return False


def require_login(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not check_login():
            login()
            return
        with st.sidebar:
            with st.expander(f"👤 {st.session_state.username}", expanded=False):
                st.caption(f"Version {VERSION}")
                if st.button("退出登录", use_container_width=True):
                    logout()
        return func(*args, **kwargs)
    return wrapper

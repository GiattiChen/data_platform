"""首页 UI 样式与组件（仅 app.py 使用）"""
import streamlit as st

from utils.constant import VERSION

GLOBAL_CSS = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

.stButton > button {
    transition: all 0.3s ease;
    border-radius: 8px;
    font-weight: 600;
    letter-spacing: 0.3px;
    min-height: 2.75rem;
    padding: 0.5rem 1.25rem;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.main-title {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-size: 2.75rem;
    font-weight: 700;
    text-align: center;
    margin-bottom: 0.5rem;
}

.feature-card {
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    padding: 1.5rem;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    margin-bottom: 0.75rem;
    min-height: 120px;
}
.feature-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
}
.feature-card h3 {
    margin: 0;
    color: white;
    font-size: 1.25rem;
}
.feature-card p {
    margin: 0.6rem 0 0;
    color: #f0f4f8;
    font-size: 0.95rem;
    line-height: 1.5;
}

.app-footer {
    text-align: center;
    padding: 1.5rem 1rem;
    color: #94a3b8;
    font-size: 0.9rem;
}
</style>
"""


def inject_global_styles():
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def render_main_title(app_name: str, version: str = VERSION):
    st.markdown(
        f'<h1 class="main-title">📝 {app_name} v{version}</h1>',
        unsafe_allow_html=True,
    )


def render_welcome(username: str):
    st.markdown(
        f"""
        <div style="text-align: center; padding: 0.5rem 0 1.5rem;">
            <h2 style="color: #1f77b4; font-size: 1.5rem; margin: 0;">
                👋 你好，{username}！
            </h2>
            <p style="color: #64748b; font-size: 1.05rem; margin-top: 0.5rem;">
                欢迎使用 Data Platform 数据管理系统
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_feature_card(title: str, description: str, gradient: str) -> str:
    return f"""
    <div class="feature-card" style="background: {gradient};">
        <h3>{title}</h3>
        <p>{description}</p>
    </div>
    """


def render_footer(app_name: str, version: str = VERSION):
    st.markdown("---")
    st.markdown(
        f"""
        <div class="app-footer">
            <strong>{app_name}</strong> · 纯文本 Pretrain & SFT 数据管理<br>
            <small>Version {version}</small>
        </div>
        """,
        unsafe_allow_html=True,
    )

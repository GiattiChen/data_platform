import streamlit as st

from core.login import require_login
from core.page import (
    display_data,
    display_data_visualization,
    display_messages,
    edit_data_form,
    manage_tags,
    register_data_form,
)
from core.storage import load_data

st.set_page_config(layout="wide", initial_sidebar_state="expanded")


@require_login
def main():
    st.title("📈 Pretrain 数据管理")
    display_messages()

    st.sidebar.header("功能导航")
    page = st.sidebar.radio(
        "选择功能",
        ["数据展示", "数据注册", "数据修改", "标签管理", "数据预览"],
    )

    if page == "数据展示":
        display_data("pretraining")
    elif page == "数据注册":
        register_data_form("pretraining")
    elif page == "标签管理":
        manage_tags("pretraining")
    elif page == "数据预览":
        display_data_visualization("pretraining")
    else:
        data = load_data("pretraining")
        if not data:
            st.info("暂无数据")
            return
        options = {f"{i+1}. {e['name']}": e for i, e in enumerate(data)}
        selected = st.selectbox("选择要修改的数据", list(options.keys()))
        edit_data_form(options[selected], "pretraining")


if __name__ == "__main__":
    main()

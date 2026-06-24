import streamlit as st
from datetime import datetime

from core.login import require_login
from core.page import display_messages
from core.storage import load_data
from core.ui import (
    inject_global_styles,
    render_feature_card,
    render_footer,
    render_main_title,
    render_welcome,
)
from utils.constant import APP_NAME, VERSION

st.set_page_config(
    page_title=APP_NAME,
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_global_styles()


def get_statistics():
    pretrain = load_data("pretraining")
    sft = load_data("sft")
    all_data = pretrain + sft
    month = datetime.now().strftime("%Y-%m")
    month_cnt = sum(1 for d in all_data if d.get("created_at", "").startswith(month))
    return {
        "total": len(all_data),
        "pretrain": len(pretrain),
        "sft": len(sft),
        "month_new": month_cnt,
    }


@require_login
def main():
    display_messages()
    render_main_title(APP_NAME, VERSION)
    render_welcome(st.session_state.username)

    with st.spinner("正在加载统计信息..."):
        stats = get_statistics()

    st.markdown("### 🎯 数据面板")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(
            "📊 数据集总数",
            f"{stats['total']} 个",
            delta=f"+{stats['month_new']} 本月",
            help="当前管理的全部数据集数量",
        )
    with c2:
        st.metric("📈 Pretrain", f"{stats['pretrain']} 个", help="预训练数据集数量")
    with c3:
        st.metric("💬 SFT", f"{stats['sft']} 个", help="SFT 数据集数量")
    with c4:
        st.metric("👤 当前用户", st.session_state.username)

    st.markdown("---")
    st.markdown("### 📋 功能模块")

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown(
            render_feature_card(
                "📈 Pretrain 数据管理",
                "数据展示、注册、修改、标签管理、文本预览",
                "radial-gradient(circle at top left, #1a365d, #2c5282, #2b6cb0)",
            ),
            unsafe_allow_html=True,
        )
        if st.button("🚀 进入 Pretrain 数据管理", key="go_pretrain", use_container_width=True, type="secondary"):
            st.switch_page("pages/1_Pretrain数据管理.py")

    with col2:
        st.markdown(
            render_feature_card(
                "💬 SFT 数据管理",
                "SFT 数据的完整生命周期管理和文本预览",
                "radial-gradient(circle at top left, #234e52, #319795, #48bb78)",
            ),
            unsafe_allow_html=True,
        )
        if st.button("🚀 进入 SFT 数据管理", key="go_sft", use_container_width=True, type="secondary"):
            st.switch_page("pages/2_SFT数据管理.py")

    render_footer(APP_NAME, VERSION)


if __name__ == "__main__":
    main()

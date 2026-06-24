"""核心业务逻辑：数据 CRUD、展示、标签管理、可视化"""
import pandas as pd
import streamlit as st

from core.data_loader import TextDataLoader, extract_text_preview
from core.storage import (
    create_dataset,
    delete_dataset,
    load_data,
    load_tags,
    save_data,
    save_tags,
    update_dataset,
)


def display_messages():
    if st.session_state.get("success_message"):
        st.success(st.session_state.pop("success_message"))


def _normalize_name(name: str) -> str:
    if not name:
        return ""
    if "/" in name:
        name = name.split("/")[-1]
    return name.lower().replace("-", "_").replace(" ", "")


def _check_duplicate(name: str, stages: list[str]) -> list[tuple[str, str]]:
    duplicates = []
    normalized = _normalize_name(name)
    for stage in stages:
        for entry in load_data(stage):
            if _normalize_name(entry["name"]) == normalized:
                duplicates.append((stage, entry["name"]))
    return duplicates


def register_data_form(default_stage: str | None = None):
    st.subheader("注册新数据")

    if "form_data" not in st.session_state:
        st.session_state.form_data = {
            "name": "",
            "source": "",
            "is_open_source": True,
            "data_size": "",
            "raw_path": "",
            "converted_path": "",
            "converted_preview_path": "",
            "registrant": st.session_state.get("username", ""),
            "process": "",
            "dynamic_tags": "",
            "data_stages": [default_stage] if default_stage else [],
            "parent_dataset": "无",
            "selected_tags": {},
        }

    fd = st.session_state.form_data
    name_outside = st.text_input("数据集名称", value=fd["name"], key="reg_name_outside")

    with st.form("register_form"):
        col1, col2 = st.columns(2)
        with col1:
            source = st.text_input("数据来源", value=fd["source"], help="如 HuggingFace 链接或内部来源")
            registrant = st.text_input("注册人", value=fd["registrant"])
            is_open_source = st.checkbox("是否开源", value=fd["is_open_source"])
        with col2:
            data_size = st.text_input("数据量", value=fd["data_size"], help="如 100万条 / 50GB")
            raw_path = st.text_input("原始数据路径", value=fd["raw_path"], help="本地绝对路径")
            converted_path = st.text_area(
                "处理后数据路径（必填，多文件换行分隔）",
                value=fd["converted_path"],
            )
            converted_preview_path = st.text_area(
                "预览文件路径（用于可视化，多文件换行分隔）",
                value=fd["converted_preview_path"],
            )

        data_stages = st.multiselect(
            "数据阶段",
            ["pretraining", "sft"],
            default=fd["data_stages"] or ([default_stage] if default_stage else []),
        )

        parent_options = ["无"]
        for stage in ["pretraining", "sft"]:
            parent_options += [e["name"] for e in load_data(stage) if e["name"] != name_outside]
        parent_options = list(dict.fromkeys(parent_options))
        parent_idx = parent_options.index(fd["parent_dataset"]) if fd["parent_dataset"] in parent_options else 0
        parent_dataset = st.selectbox("父数据集", parent_options, index=parent_idx)

        process = st.text_area("处理流程/备注", value=fd["process"])
        dynamic_tags = st.text_input("备注标签（选填）", value=fd["dynamic_tags"], help="如：金融语料、高质量清洗")

        tags_config = load_tags()
        selected_tags = {}
        for dimension, tag_list in tags_config.items():
            default_vals = fd.get("selected_tags", {}).get(dimension, [])
            selected_tags[dimension] = st.multiselect(f"{dimension}", tag_list, default=default_vals)

        submitted = st.form_submit_button("提交注册", type="primary")

        if submitted:
            name = name_outside
            if not name or not source or not registrant or not converted_path or not data_stages:
                missing = []
                if not name:
                    missing.append("数据集名称")
                if not source:
                    missing.append("数据来源")
                if not registrant:
                    missing.append("注册人")
                if not converted_path:
                    missing.append("处理后数据路径")
                if not data_stages:
                    missing.append("数据阶段")
                st.error(f"请填写必填字段：{', '.join(missing)}")
                return

            duplicates = _check_duplicate(name, data_stages)
            if duplicates:
                msg = "发现重复数据：\n" + "\n".join(f"- {s}: {n}" for s, n in duplicates)
                st.warning(msg)
                return

            for dim in tags_config:
                if not selected_tags.get(dim):
                    selected_tags[dim] = ["☀️ unknown"]

            entry = {
                "name": name,
                "source": source,
                "registrant": registrant,
                "is_open_source": is_open_source,
                "data_size": data_size,
                "raw_path": raw_path,
                "converted_path": converted_path,
                "converted_preview_path": converted_preview_path,
                "process": process,
                "dynamic_tags": dynamic_tags,
                "tags": selected_tags,
                "parent_dataset": parent_dataset,
                "stages": data_stages,
            }

            try:
                create_dataset(entry, data_stages)
                st.session_state.success_message = f"数据 '{name}' 注册成功！"
                st.rerun()
            except ValueError as e:
                st.error(str(e))


def edit_data_form(entry: dict, stage: str):
    with st.form(f"edit_{entry['_id']}"):
        st.subheader(f"编辑: {entry['name']}")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("数据集名称", value=entry["name"])
            source = st.text_input("数据来源", value=entry["source"])
            registrant = st.text_input("注册人", value=entry["registrant"])
            is_open_source = st.checkbox("是否开源", value=entry.get("is_open_source", False))
        with col2:
            data_size = st.text_input("数据量", value=entry.get("data_size", ""))
            raw_path = st.text_input("原始数据路径", value=entry.get("raw_path", ""))
            converted_path = st.text_area("处理后数据路径", value=entry.get("converted_path", ""))
            converted_preview_path = st.text_area("预览文件路径", value=entry.get("converted_preview_path", ""))

        data_stages = st.multiselect("数据阶段", ["pretraining", "sft"], default=entry.get("stages", [stage]))
        process = st.text_area("处理流程/备注", value=entry.get("process", ""))
        dynamic_tags = st.text_input("备注标签", value=entry.get("dynamic_tags", ""))

        tags_config = load_tags()
        selected_tags = {}
        for dimension, tag_list in tags_config.items():
            current = entry.get("tags", {}).get(dimension, [])
            selected_tags[dimension] = st.multiselect(dimension, tag_list, default=current)

        col_save, col_del = st.columns(2)
        save_btn = col_save.form_submit_button("保存修改", type="primary")
        del_btn = col_del.form_submit_button("删除数据集", type="secondary")

        if save_btn:
            for dim in tags_config:
                if not selected_tags.get(dim):
                    selected_tags[dim] = ["☀️ unknown"]
            updated = {
                "name": name,
                "source": source,
                "registrant": registrant,
                "is_open_source": is_open_source,
                "data_size": data_size,
                "raw_path": raw_path,
                "converted_path": converted_path,
                "converted_preview_path": converted_preview_path,
                "process": process,
                "dynamic_tags": dynamic_tags,
                "tags": selected_tags,
                "stages": data_stages,
            }
            try:
                update_dataset(entry["_id"], updated, data_stages)
                st.session_state.success_message = f"数据 '{name}' 更新成功！"
                st.rerun()
            except ValueError as e:
                st.error(str(e))

        if del_btn:
            try:
                delete_dataset(entry["_id"], stage)
                st.session_state.success_message = f"数据 '{entry['name']}' 已删除"
                st.rerun()
            except ValueError as e:
                st.error(str(e))


def display_data(stage: str):
    data = load_data(stage)
    if not data:
        st.info("暂无数据，请先注册")
        return

    st.write("### 数据列表")
    tags_config = load_tags()
    filters = {}

    dimensions = list(tags_config.keys())
    cols = st.columns(min(3, len(dimensions) + 2))
    for idx, dim in enumerate(dimensions):
        with cols[idx % len(cols)]:
            filters[dim] = st.multiselect(f"筛选 {dim}", tags_config[dim])

    name_filter = st.text_input("按名称筛选")
    tag_filter = st.text_input("按备注标签筛选")

    filtered = data
    if name_filter:
        nf = _normalize_name(name_filter)
        filtered = [e for e in filtered if nf in _normalize_name(e["name"])]
    if tag_filter:
        filtered = [e for e in filtered if tag_filter.lower() in e.get("dynamic_tags", "").lower()]
    for dim, selected in filters.items():
        if selected:
            if "🌟 ALL" in selected:
                continue
            filtered = [e for e in filtered if any(t in e.get("tags", {}).get(dim, []) for t in selected)]

    if not filtered:
        st.info("没有符合筛选条件的数据")
        return

    rows = []
    for i, entry in enumerate(filtered):
        row = {"序号": i + 1, "数据集名称": entry["name"]}
        for dim, vals in entry.get("tags", {}).items():
            row[dim] = ", ".join(vals)
        row.update({
            "备注标签": entry.get("dynamic_tags", ""),
            "数据路径": entry.get("converted_path", ""),
            "预览路径": entry.get("converted_preview_path", ""),
            "数据来源": entry["source"],
            "开源": "✅" if entry.get("is_open_source") else "❌",
            "数据量": entry.get("data_size", ""),
            "注册人": entry.get("registrant", ""),
            "创建时间": entry.get("created_at", ""),
            "更新时间": entry.get("updated_at", ""),
        })
        rows.append(row)

    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True, height=600)


def manage_tags(stage: str):
    st.subheader("标签维度管理")
    tags = load_tags()

    with st.expander("添加新维度"):
        with st.form("add_dim"):
            dim_name = st.text_input("维度名称")
            dim_values = st.text_area("标签值（每行一个）")
            if st.form_submit_button("添加"):
                if dim_name and dim_values:
                    if dim_name in tags:
                        st.error("维度已存在")
                    else:
                        vals = [v.strip() for v in dim_values.split("\n") if v.strip()]
                        if "☀️ unknown" not in vals:
                            vals.append("☀️ unknown")
                        if "🌟 ALL" not in vals:
                            vals.append("🌟 ALL")
                        tags[dim_name] = vals
                        save_tags(tags)
                        data = load_data(stage)
                        for entry in data:
                            entry.setdefault("tags", {})[dim_name] = ["☀️ unknown"]
                        save_data(stage, data)
                        st.session_state.success_message = f"维度 '{dim_name}' 添加成功"
                        st.rerun()

    with st.expander("编辑维度"):
        dim = st.selectbox("选择维度", list(tags.keys()))
        if dim:
            with st.form("edit_dim"):
                new_vals = st.text_area("标签值（每行一个）", value="\n".join(tags[dim]))
                if st.form_submit_button("保存"):
                    vals = [v.strip() for v in new_vals.split("\n") if v.strip()]
                    tags[dim] = vals
                    save_tags(tags)
                    st.session_state.success_message = f"维度 '{dim}' 已更新"
                    st.rerun()

    st.markdown("#### 当前标签配置")
    for dim, vals in tags.items():
        st.markdown(f"**{dim}**: {', '.join(vals)}")


def display_data_visualization(stage: str):
    st.subheader("文本数据预览")
    loader = TextDataLoader(max_samples=15)

    tab1, tab2 = st.tabs(["从已注册数据选择", "直接输入路径"])

    with tab1:
        data = load_data(stage)
        if not data:
            st.info("暂无数据")
        else:
            options = {f"{i+1}. {e['name']}": e for i, e in enumerate(data)}
            selected = st.selectbox("选择数据集", list(options.keys()))
            entry = options[selected]
            preview_paths = [p.strip() for p in entry.get("converted_preview_path", "").split("\n") if p.strip()]
            if not preview_paths:
                preview_paths = [p.strip() for p in entry.get("converted_path", "").split("\n") if p.strip()]

            if preview_paths:
                path = preview_paths[0] if len(preview_paths) == 1 else st.selectbox("选择预览文件", preview_paths)
                if st.button("加载预览", key="preview_registered"):
                    _render_preview(loader, path)
            else:
                st.warning("该数据集未配置预览路径")

    with tab2:
        custom_path = st.text_input("输入本地 JSONL/JSON 文件路径")
        if st.button("加载预览", key="preview_custom") and custom_path:
            _render_preview(loader, custom_path)


def _render_preview(loader: TextDataLoader, path: str):
    try:
        with st.spinner("加载中..."):
            samples = loader.load_samples(path)
        st.success(f"成功加载 {len(samples)} 条样本（最多展示 {loader.max_samples} 条）")
        for i, item in enumerate(samples):
            with st.expander(f"样本 {i + 1}", expanded=(i < 3)):
                st.markdown(extract_text_preview(item))
                with st.popover("查看原始 JSON"):
                    st.json(item)
    except (ValueError, OSError) as e:
        st.error(str(e))

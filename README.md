# Data Platform

数据管理系统（`data_management_app` 的精简版），仅保留 Pretrain 和 SFT 两个模块。

## 功能

- **Pretrain 数据管理**：预训练语料的注册、查询、修改、删除
- **SFT 数据管理**：SFT 对话/指令数据的完整生命周期管理
- **标签管理**：文本领域分类（内容形态 / 领域 / 语言）
- **文本预览**：从本地 JSONL 文件加载并预览纯文本样本

## 与原版的差异

| 特性 | 原版 data_management_app | 本版本 |
|------|-------------------------|--------|
| 数据模态 | 多模态（图文音视频） | 纯文本 |
| 存储后端 | 外部 Meta Service + BOS | 本地 JSON 文件 |
| 数据地址 | BOS / 本地 / S3 | 仅本地直接路径 |
| 模块 | 6+ 页面 | 2 个核心模块 |
| 标签体系 | 数据模态 + 细分类型 | 内容形态 + 领域 + 语言 |

## 快速开始

```bash
cd data_platform
pip install -r requirements.txt
streamlit run app.py
# 或
bash start.sh
```

默认端口：**8730**

默认账号见 `credentials.txt.example`（需复制为 `credentials.txt` 后自行配置）

## 项目结构

```
data_platform/
├── app.py                  # 首页仪表盘
├── pages/
│   ├── 1_Pretrain数据管理.py
│   └── 2_SFT数据管理.py
├── core/
│   ├── storage.py          # 本地 JSON 存储
│   ├── page.py             # 业务逻辑
│   ├── data_loader.py      # 文本 JSONL 加载
│   └── login.py            # 登录认证
├── data/                   # 数据集元信息（JSON）
├── mock_samples/           # Mock 预览数据
└── credentials.txt         # 用户凭证
```

## 数据字段

| 字段 | 说明 | 必填 |
|------|------|------|
| name | 数据集名称 | ✅ |
| source | 数据来源 | ✅ |
| registrant | 注册人 | ✅ |
| converted_path | 处理后数据路径 | ✅ |
| converted_preview_path | 预览文件路径 | |
| raw_path | 原始数据路径 | |
| data_size | 数据量 | |
| is_open_source | 是否开源 | |
| process | 处理流程/备注 | |
| dynamic_tags | 自由备注标签 | |
| tags | 结构化标签（内容形态/领域/语言） | |
| parent_dataset | 父数据集 | |

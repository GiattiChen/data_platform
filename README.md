# Data Platform

数据管理系统，支持 Pretrain 和 SFT 两个模块。

## 功能

- **Pretrain 数据管理**：预训练语料的注册、查询、修改、删除
- **SFT 数据管理**：SFT 对话/指令数据的完整生命周期管理
- **标签管理**：文本领域分类（内容形态 / 领域 / 语言）
- **文本预览**：从本地 JSONL 文件加载并预览纯文本样本

## 快速开始

### 本地启动

```bash
cd data_platform
pip install -r requirements.txt
cp credentials.txt.example credentials.txt   # 按需修改账号密码
streamlit run app.py
# 或
bash start.sh
```

- 默认端口：**8730**
- 本机访问：`http://localhost:8730`
- 局域网访问（需已配置 `address = "0.0.0.0"`）：`http://<你的局域网IP>:8730`
- 默认账号：`admin` / `admin123` 或 `demo` / `demo123`

### 公网临时访问（内网穿透）

适合给外网用户临时演示，无需配置路由器端口转发。

```bash
# 终端 1：启动应用
cd data_platform
streamlit run app.py

# 终端 2：启动隧道（需先安装 cloudflared）
brew install cloudflared   # 首次使用需安装
bash start_tunnel.sh
```

终端 2 会输出类似 `https://xxx.trycloudflare.com` 的临时公网地址，分享给他人即可访问。**保持该终端运行**，关闭后链接失效。

> 注意：公网暴露时当前为明文账号密码鉴权，仅建议用于内部演示，勿用于生产环境。

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
├── credentials.txt.example # 凭证模板（复制为 credentials.txt）
└── credentials.txt         # 用户凭证（本地配置，不提交 Git）
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

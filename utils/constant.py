"""纯文本数据管理应用常量定义"""
from pathlib import Path

VERSION = "1.0.0"
APP_NAME = "Data Platform"

DATA_DIR = Path("data")
MOCK_SAMPLES_DIR = Path("mock_samples")
LOGIN_STATE_DIR = Path("./.login_states")
CREDENTIAL_FILE_PATH = Path("./credentials.txt")
AUTH_TOKEN_KEY = "data_platform_auth_token"

# 纯文本领域标签维度默认值
# 注意：数据大类（Pretrain / SFT）由模块本身区分，标签不再重复表达阶段信息
DEFAULT_TAGS = {
    "内容形态": [
        "连续篇章", "百科/知识条目", "新闻稿件",
        "单轮问答", "多轮对话", "指令跟随",
        "代码", "数学推理", "推理链CoT",
        "☀️ unknown", "🌟 ALL",
    ],
    "领域": [
        "通用", "金融", "法律", "医疗", "科技", "教育", "电商", "政务",
        "☀️ unknown", "🌟 ALL",
    ],
    "语言": [
        "ZH", "EN", "多语言",
        "☀️ unknown", "🌟 ALL",
    ],
}

STAGE_MAPPING = {
    "pretraining": "Pretrain",
    "sft": "SFT",
}

# 文本 JSONL 常见字段
TEXT_CONTENT_FIELDS = [
    "text", "content", "conversations", "messages",
    "query", "response", "instruction", "input", "output",
    "prompt", "completion", "caption",
]

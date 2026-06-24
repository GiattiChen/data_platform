"""纯文本 JSONL 数据加载与预览"""
import json
import os
import random
from pathlib import Path

from utils.constant import TEXT_CONTENT_FIELDS

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TextDataLoader:
    """从本地文件路径加载纯文本 JSONL 数据"""

    def __init__(self, max_samples: int = 20):
        self.max_samples = max_samples

    def resolve_path(self, path: str) -> str:
        path = path.strip()
        if not path:
            raise ValueError("路径不能为空")
        if path.startswith(("bos://", "bos:/", "s3://", "s3:/")):
            raise ValueError("不支持 BOS/S3 路径，请使用本地文件路径")
        if not os.path.isabs(path):
            path = str(PROJECT_ROOT / path)
        if os.path.isdir(path):
            for fname in sorted(os.listdir(path)):
                if fname.endswith((".jsonl", ".json")):
                    return os.path.join(path, fname)
            raise ValueError(f"目录 {path} 中未找到 JSON/JSONL 文件")
        if not os.path.exists(path):
            raise ValueError(f"文件不存在: {path}")
        return path

    def load_samples(self, path: str) -> list[dict]:
        resolved = self.resolve_path(path)
        samples = []
        with open(resolved, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    samples.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        if len(samples) > self.max_samples:
            samples = random.sample(samples, self.max_samples)
        return samples


def extract_text_preview(item: dict) -> str:
    """从一条记录中提取可读的文本预览"""
    if "conversations" in item:
        lines = []
        for turn in item["conversations"]:
            role = turn.get("from") or turn.get("role", "unknown")
            value = turn.get("value") or turn.get("content", "")
            lines.append(f"**{role}**: {value}")
        return "\n\n".join(lines)

    if "messages" in item:
        lines = []
        for msg in item["messages"]:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            lines.append(f"**{role}**: {content}")
        return "\n\n".join(lines)

    if "query" in item and "response" in item:
        return f"**query**: {item['query']}\n\n**response**: {item['response']}"

    if "instruction" in item:
        parts = [f"**instruction**: {item['instruction']}"]
        if "input" in item:
            parts.append(f"**input**: {item['input']}")
        if "output" in item:
            parts.append(f"**output**: {item['output']}")
        return "\n\n".join(parts)

    if "text" in item:
        return item["text"]

    if "content" in item and isinstance(item["content"], str):
        return item["content"]

    for field in TEXT_CONTENT_FIELDS:
        if field in item and isinstance(item[field], str):
            return item[field]

    return json.dumps(item, ensure_ascii=False, indent=2)

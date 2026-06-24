"""本地 JSON 存储层"""
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from utils.constant import DATA_DIR, DEFAULT_TAGS

DATA_DIR.mkdir(exist_ok=True)

STAGE_FILES = {
    "pretraining": DATA_DIR / "pretraining_data.json",
    "sft": DATA_DIR / "sft_data.json",
}
TAGS_FILE = DATA_DIR / "tags.json"


def _read_json(path: Path, default: Any) -> Any:
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default


def _write_json(path: Path, data: Any) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_tags() -> dict[str, list[str]]:
    return _read_json(TAGS_FILE, DEFAULT_TAGS.copy())


def save_tags(tags: dict[str, list[str]]) -> None:
    _write_json(TAGS_FILE, tags)


def load_data(stage: str) -> list[dict]:
    path = STAGE_FILES.get(stage)
    if not path:
        raise ValueError(f"不支持的阶段: {stage}")
    return _read_json(path, [])


def save_data(stage: str, datasets: list[dict]) -> None:
    path = STAGE_FILES.get(stage)
    if not path:
        raise ValueError(f"不支持的阶段: {stage}")
    _write_json(path, datasets)


def create_dataset(entry: dict, stages: list[str]) -> None:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry.setdefault("_id", str(uuid.uuid4()))
    entry.setdefault("created_at", now)
    entry["updated_at"] = now

    for stage in stages:
        data = load_data(stage)
        if any(d["name"].lower().replace("-", "_") == entry["name"].lower().replace("-", "_") for d in data):
            raise ValueError(f"数据集 '{entry['name']}' 在 {stage} 中已存在")
        data.append(entry.copy())
        save_data(stage, data)


def update_dataset(entry_id: str, updated: dict, stages: list[str]) -> None:
    updated["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    found = False
    for stage in stages:
        data = load_data(stage)
        for i, item in enumerate(data):
            if item.get("_id") == entry_id:
                data[i] = {**item, **updated, "_id": entry_id}
                save_data(stage, data)
                found = True
                break
    if not found:
        raise ValueError("未找到要更新的数据集")


def delete_dataset(entry_id: str, stage: str) -> None:
    data = load_data(stage)
    new_data = [d for d in data if d.get("_id") != entry_id]
    if len(new_data) == len(data):
        raise ValueError("未找到要删除的数据集")
    save_data(stage, new_data)


def find_dataset_by_id(entry_id: str) -> dict | None:
    for stage in STAGE_FILES:
        for item in load_data(stage):
            if item.get("_id") == entry_id:
                return item
    return None

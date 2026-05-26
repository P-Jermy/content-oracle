"""
Content Oracle 状态管理模块
处理 .content-state.json 的读写和项目目录结构
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

STATE_SCHEMA_VERSION = "0.1.0"

DEFAULT_STATE = {
    "schema_version": STATE_SCHEMA_VERSION,
    "skill_version": "0.1.0",
    "initialized_at": None,
    "rubric_version": "v0",
    "rubric_form": "default",
    "content_form": "long-essay",
    "typical_duration_seconds": None,
    "target_publish_cadence_days": 3,
    "benchmark_status": "not-setup",
    "benchmark_name": None,
    "benchmark_sample_count": 0,
    "calibration_samples": 0,
    "data_collection": "manual",
    "pool_status": "markdown",
    "enabled_trend_sources": ["github-trending", "hacker-news"],
    "enabled_perf_adapters": [],
    "last_trends_run_at": None,
    "last_trends_added_count": 0,
    "last_published_at": None,
    "last_published_file": None,
    "shoots": [],
    "pending_retros": [],
    "consecutive_directional_errors": [],
    "in_progress_session": None,
    "hooks_enabled": True,
}


def find_project_root(path: Optional[str] = None) -> Optional[str]:
    """从当前或指定目录向上查找 .content-state.json"""
    start = Path(path or os.getcwd()).resolve()
    for parent in [start] + list(start.parents):
        state_file = parent / ".content-state.json"
        if state_file.exists():
            return str(parent)
    return None


def load_state(project_dir: Optional[str] = None) -> dict:
    """加载项目状态，不存在则返回默认值"""
    if project_dir:
        state_file = Path(project_dir) / ".content-state.json"
    else:
        root = find_project_root()
        if not root:
            return dict(DEFAULT_STATE)
        state_file = Path(root) / ".content-state.json"

    if state_file.exists():
        with open(state_file) as f:
            return json.load(f)
    return dict(DEFAULT_STATE)


def save_state(state: dict, project_dir: str):
    """保存项目状态"""
    state_file = Path(project_dir) / ".content-state.json"
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def init_project(project_dir: str, content_form: str = "long-essay", rubric: str = "default"):
    """初始化一个新内容项目"""
    project = Path(project_dir)
    dirs = [
        project / "articles",
        project / "scripts",
        project / "predictions",
        project / ".content-cache",
    ]
    state = dict(DEFAULT_STATE)
    now = datetime.utcnow().isoformat() + "Z"
    state["schema_version"] = STATE_SCHEMA_VERSION
    state["initialized_at"] = now
    state["content_form"] = content_form
    state["rubric_form"] = rubric

    save_state(state, project_dir)

    # create empty candidates.md
    candidates = project / "candidates.md"
    if not candidates.exists():
        with open(candidates, "w", encoding="utf-8") as f:
            f.write("# 选题池\n\n")
            f.write("<!-- 每行一个候选选题，格式：- [优先级] 标题 | 来源 | 理由 -->\n")

    return state

#!/usr/bin/env python3
"""
Content Oracle - predict
盲预测：在发布前打分、写预测记录（不可修改）
"""

import os
import sys
import argparse
import hashlib
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.state import find_project_root, load_state, save_state
from scripts.score import RUBRIC_DIMENSIONS


PREDICTION_TEMPLATE = """# 预测报告

> 盲预测 — 编写于 {timestamp}
> **预测不可修改。** 发布后数据到来时追加到 ## 复盘 段。

## 稿件信息

- **文件名**: {filename}
- **字数**: {word_count}
- **内容形态**: {content_form}

## 盲预测（{prediction_id}）

### 评分

{dimensions_scores}

### 综合评分

- **Composite**: {composite:.1f}/10
- **置信度**: {confidence}/10

### 一句话预测

{prediction_statement}

### 预测 bucket

| 范围 | 概率 |
|------|------|
| 优秀 (>8.5) | {bucket_great}% |
| 良好 (6.5-8.5) | {bucket_good}% |
| 普通 (4-6.5) | {bucket_avg}% |
| 不佳 (<4) | {bucket_poor}% |

## 复盘

<!-- 发布 3 天后填入真实数据 -->
"""


def generate_prediction_id(draft_path: str) -> str:
    """生成唯一预测 ID"""
    raw = f"{draft_path}:{datetime.now(timezone.utc).isoformat()}"
    return hashlib.sha256(raw.encode()).hexdigest()[:12]


def main():
    parser = argparse.ArgumentParser(description="盲预测")
    parser.add_argument("draft_path", help="草稿文件路径")
    parser.add_argument("--project-dir", help="内容项目目录（默认自动查找）")
    parser.add_argument("--form", default="long-essay", help="内容形态")
    parser.add_argument("--confidence", type=int, default=7, help="置信度 1-10")
    parser.add_argument("--prediction", default="", help="一句话预测")
    parser.add_argument("--composite", type=float, default=0, help="综合评分")
    args = parser.parse_args()

    project_dir = args.project_dir or find_project_root()
    if not project_dir:
        print("❌ 未找到 .content-state.json，请先运行初始化")
        sys.exit(1)

    # 校验草稿
    draft_path = os.path.abspath(args.draft_path)
    if not os.path.exists(draft_path):
        print(f"❌ 草稿不存在: {draft_path}")
        sys.exit(1)

    with open(draft_path) as f:
        content = f.read()

    word_count = len(content)
    filename = os.path.basename(draft_path)
    prediction_id = generate_prediction_id(draft_path)

    # 评分
    scores_text = ""
    total = 0
    for i, dim in enumerate(RUBRIC_DIMENSIONS, 1):
        scores_text += f"- **{i}. {dim}**: 7/10\n"
        total += 7

    composite = args.composite if args.composite > 0 else round(total / len(RUBRIC_DIMENSIONS), 1)
    if not args.prediction:
        args.prediction = "这条内容会达到预期效果"

    # 生成预测文件
    pred_filename = f"{datetime.now(timezone.utc).strftime('%Y-%m-%d')}_{prediction_id}_{filename.rsplit('.',1)[0][:30]}.md"
    pred_dir = Path(project_dir) / "predictions"
    pred_dir.mkdir(exist_ok=True)
    pred_path = pred_dir / pred_filename

    content_form = args.form
    bucket = {
        "great": 15,
        "good": 40,
        "avg": 35,
        "poor": 10,
    }

    pred_content = PREDICTION_TEMPLATE.format(
        timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        filename=filename,
        word_count=word_count,
        content_form=content_form,
        dimensions_scores=scores_text,
        composite=composite,
        confidence=args.confidence,
        prediction_id=prediction_id,
        prediction_statement=args.prediction,
        **{f"bucket_{k}": v for k, v in bucket.items()},
    )

    with open(pred_path, "w", encoding="utf-8") as f:
        f.write(pred_content)

    # 更新 state
    state = load_state(project_dir)
    now = datetime.now(timezone.utc).isoformat()
    state["in_progress_session"] = {
        "type": "prediction",
        "file": str(pred_path),
        "started_at": now,
    }
    save_state(state, project_dir)

    print(f"✅ 盲预测已保存: {pred_path}")
    print()
    print(f"📊 Composite: {composite}/10 | 置信度: {args.confidence}/10")
    print(f"   {args.prediction}")
    print()
    print("发布后说 '已发布 <预测文件>' 登记发布")
    print("3 天后说 '复盘 <预测文件>' 填写真实数据")


if __name__ == "__main__":
    main()

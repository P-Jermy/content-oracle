#!/usr/bin/env python3
"""
content-score-blind: 盲打分（内部子代理）
NOT user-facing. 接收 script_path + rubric_path → 返回 9 维度 JSON 评分
"""
import os, sys, json, re, argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.state import find_project_root, load_state

DIMS = [
    "novelty", "depth", "actionability", "timeliness",
    "clarity", "engagement", "credibility", "relevance", "craft"
]

def main():
    parser = argparse.ArgumentParser(description="盲打分（内部使用）")
    parser.add_argument("--script", required=True, help="脚本路径")
    parser.add_argument("--rubric", help="rubric_notes.md 路径")
    parser.add_argument("--output", help="输出到文件")
    args = parser.parse_args()

    if not os.path.exists(args.script):
        print(json.dumps({"error": f"script not found: {args.script}"}))
        sys.exit(1)

    with open(args.script, encoding='utf-8') as f:
        content = f.read()
    
    score = {
        "script": args.script,
        "length_chars": len(content),
        "dimensions": {},
        "composite": 0.0,
    }

    # Read rubric if available
    rubric_text = ""
    if args.rubric and os.path.exists(args.rubric):
        with open(args.rubric, encoding='utf-8') as f:
            rubric_text = f.read()

    for d in DIMS:
        score["dimensions"][d] = {
            "score": 3,
            "confidence": "medium",
            "reason": "auto-generated placeholder"
        }

    score["composite"] = round(sum(v["score"] for v in score["dimensions"].values()) / len(DIMS), 1)
    
    out = json.dumps(score, ensure_ascii=False, indent=2)
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(out)
        print(f"✅ 评分已保存: {args.output}")
    else:
        print(out)

if __name__ == "__main__":
    main()

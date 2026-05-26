#!/usr/bin/env python3
"""
content-status: 状态面板
读取项目状态 + 扫描文件系统 → 输出当前概览和建议
"""
import os, sys, json, re, argparse
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.state import find_project_root, load_state

def main():
    parser = argparse.ArgumentParser(description="状态面板")
    parser.add_argument("--project-dir", help="项目目录")
    parser.add_argument("--json", action="store_true", help="JSON输出")
    args = parser.parse_args()

    project_dir = args.project_dir or find_project_root()
    if not project_dir:
        print("❌ 未找到项目")
        sys.exit(1)

    state = load_state(project_dir)

    # Scan file system
    articles = []
    arts_dir = os.path.join(project_dir, "articles")
    if os.path.exists(arts_dir):
        articles = [f for f in sorted(os.listdir(arts_dir)) if f.endswith('.md')]

    scripts = []
    scr_dir = os.path.join(project_dir, "scripts")
    if os.path.exists(scr_dir):
        scripts = [f for f in sorted(os.listdir(scr_dir)) if f.endswith('.md')]

    predictions = []
    pred_dir = os.path.join(project_dir, "predictions")
    if os.path.exists(pred_dir):
        predictions = [f for f in sorted(os.listdir(pred_dir)) if f.endswith('.md')]

    candidates = []
    cand_path = os.path.join(project_dir, "candidates.md")
    if os.path.exists(cand_path):
        with open(cand_path, encoding='utf-8') as f:
            lines = f.readlines()
        for line in lines:
            if line.startswith('- ['):
                candidates.append(line.strip())

    # Count rubric dimensions
    rubric_path = os.path.join(project_dir, "rubric_notes.md")
    rubric_dims = 0
    if os.path.exists(rubric_path):
        with open(rubric_path, encoding='utf-8') as f:
            content = f.read()
        rubric_dims = len(re.findall(r'^##\s+\d+\.?\s', content, re.MULTILINE))

    if args.json:
        info = {
            "project": project_dir,
            "schema_version": state.get("schema_version"),
            "rubric_version": state.get("rubric_version", "v0"),
            "content_form": state.get("content_form", "long-essay"),
            "calibration_samples": state.get("calibration_samples", 0),
            "rubric_dims": rubric_dims,
            "articles": len(articles),
            "scripts": len(scripts),
            "predictions": len(predictions),
            "candidates": len(candidates),
            "trend_sources": state.get("enabled_trend_sources", []),
            "last_published": state.get("last_published_at", None),
        }
        print(json.dumps(info, ensure_ascii=False, indent=2))
        return

    # Human output
    print(f"""
╔══════════════════════════════════════╗
║   Content Oracle  状态面板           ║
╚══════════════════════════════════════╝

项目: {os.path.basename(project_dir)}
Schema: {state.get('schema_version','?')} | Rubric: {state.get('rubric_version','v0')}
形态: {state.get('content_form','long-essay')}

📦 内容仓库
   文章: {len(articles)} 篇
   草稿: {len(scripts)} 个
   预测: {len(predictions)} 个
   候选: {len(candidates)} 个

📐 Rubric
   维度: {rubric_dims}
   校准样本: {state.get('calibration_samples', 0)}
   池状态: {state.get('pool_status', 'markdown')}

📡 数据源
   启用: {', '.join(state.get('enabled_trend_sources', ['(无)']))}
   最近采集: {state.get('last_trends_run_at', '从未')[:19] if state.get('last_trends_run_at') else '从未'}

📤 发布
   最近: {state.get('last_published_at', '从未')[:19] if state.get('last_published_at') else '从未'}

💡 建议:
""")

    if len(candidates) < 3:
        print("   • 选题池不足（<3），试试'抓热点'补充")
    if rubric_dims == 0:
        print("   • Rubric 未配置，试试'打分本篇'初始化")
    if state.get('calibration_samples', 0) >= 5 and state.get('rubric_version') != 'v1':
        print("   • 校准样本≥5，可考虑升级rubric（bump）")
    if state.get('pending_retros'):
        print(f"   • 待复盘 {len(state.get('pending_retros',[]))} 篇")
    if len(articles) > 0:
        print(f"   • 最新文章: {articles[-1] if articles else '(无)'}")
    print()

if __name__ == "__main__":
    main()

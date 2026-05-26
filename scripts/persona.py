#!/usr/bin/env python3
"""
content-persona: 读者画像
从已发布文章 + 预测数据，提取读者画像 → audience.md
"""
import os, sys, json, re, argparse
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.state import find_project_root, load_state

def main():
    parser = argparse.ArgumentParser(description="读者画像")
    parser.add_argument("--project-dir", help="项目目录")
    parser.add_argument("--rebuild", action="store_true", help="重新生成")
    parser.add_argument("--show", action="store_true", help="显示当前 audience.md")
    args = parser.parse_args()

    project_dir = args.project_dir or find_project_root()
    if not project_dir:
        print("❌ 未找到项目")
        sys.exit(1)

    audience_path = os.path.join(project_dir, "audience.md")

    if args.show:
        if os.path.exists(audience_path):
            with open(audience_path, encoding='utf-8') as f:
                print(f.read())
        else:
            print("❌ audience.md 不存在，请先用 --rebuild 生成")
        return

    if args.rebuild or not os.path.exists(audience_path):
        # Scan articles for clues
        articles_dir = os.path.join(project_dir, "articles")
        article_titles = []
        if os.path.exists(articles_dir):
            for f in sorted(os.listdir(articles_dir)):
                if f.endswith('.md'):
                    # Read first line for title
                    with open(os.path.join(articles_dir, f), encoding='utf-8') as af:
                        first = af.readline().strip()
                        article_titles.append(first.replace('#','').strip() or f)
        
        # Generate audience profile template
        content = f"""# 读者画像

> 自动生成于 {datetime.now().strftime('%Y-%m-%d')}

## 受众概况

基于 {len(article_titles)} 篇已发表文章：

"""
        for t in article_titles:
            content += f"- {t}\n"

        content += """
## 读者特征（待补充）

- 职业：
- 技术栈：
- 阅读偏好：
- 痛点：
- 语言风格：

## 撰写准则

1.
2.
3.

## 反模式（读者不喜欢的）

1.
2.
"""
        with open(audience_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ audience.md 已生成（{len(article_titles)} 篇文章参考）")
        print("请手动补充读者特征和撰写准则")
    else:
        print(f"audience.md 已存在。使用 --rebuild 重新生成")

if __name__ == "__main__":
    main()

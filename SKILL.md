---
name: content-oracle
description: >-
  把内容创作变成可校准的预测循环。打分 → 盲预测 → 发布 → T+N 天复盘 → 进化 rubric。
  通用方法论，不限平台/形态（公众号、视频、播客、X thread 等均适用）。
  触发词：初始化 | 抓热点 | 推荐选题 | 打分这篇 | 盲预测 | 复盘 | 状态 | 升级rubric
version: 0.1.0
---

# Content Oracle / 内容先知

> 把每次"我感觉这条会爆"变成可校准的实验。

## 方法论

**打分 → 盲预测 → 发布 → 复盘 → 进化**

每发一条内容，你对"什么能火"的判断就校准一次。三个月后，你有一份**只属于你的爆款公式**。

## 三条不可妥协原则

1. **盲预测**：预测必须在看到实绩数据**之前**写完。一旦写完不可篡改——只能追加复盘。
2. **升级 = 全量重打**：rubric 升级时，所有有实绩的样本需用新公式重新打分对比通过。
3. **rubric 是工作台不是博物馆**：被推翻/过时的观察删掉，不保留考古层。

## 路由表

| 你说 | 调用 | 前置条件 |
|------|------|----------|
| "初始化" / "init" | `scripts/init.py` | 无（入口） |
| "抓热点" / "trends" / "今天有什么可做的" | `scripts/trends.py` | 已 init |
| "推荐选题" / "recommend" / "next topic" | `scripts/recommend.py` | 有 candidates.md |
| "打分这篇 [path]" / "score this [path]" | `scripts/score.py` | rubric_notes.md 存在 |
| "盲预测 [path]" / "predict [path]" | `scripts/predict.py` | 已 init + 有最终稿 |
| "已发布 [path]" / "published [path]" | `scripts/publish.py` | 对应预测文件存在 |
| "复盘 [path]" / "retro [path]" / "T+3d" | `scripts/retro.py` | 对应预测文件存在 |
| "状态" / "status" | `scripts/status.py` | 任意时刻 |
| "升级 rubric" / "bump" | `scripts/bump.py` | 校准池 ≥ 最小样本数 |

## 项目目录结构

用户在内容项目目录中运行 `content-init` 后，会生成：

```
<content-project>/
├── .content-state.json        # 状态文件
├── .content-cache/            # 缓存（不入版本）
├── rubric_notes.md            # 评分规则（真实来源）
├── candidates.md              # 选题池
├── scripts/                   # 草稿
├── predictions/               # 盲预测记录（不可变）
├── content.db                 # 可选 SQLite 校准池

---
name: content-oracle
description: >-
  把内容创作变成可校准的预测循环。打分 → 盲预测 → 发布 → T+N 天复盘 → 进化 rubric。
  通用方法论，不限平台/形态（公众号、视频、播客、X thread 等均适用）。
  触发词：初始化 | 抓热点 | 推荐选题 | 打分本篇 | 写稿 | 盲预测 | 发布 | 复盘 | 状态 | 升级rubric | 种子选题 | 读者画像 | 对标学习 | 迁移
version: 0.2.0
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
| "打分本篇 [path]" / "score this [path]" | `scripts/score.py` | rubric_notes.md 存在 |
| "写稿" / "shoot" / "写 [title]" | `scripts/shoot.py` | 有候选选题 |
| "盲预测 [path]" / "predict [path]" | `scripts/predict.py` | 已 init + 有最终稿 |
| "发布" / "publish [path]" / "已发布 [path]" | `scripts/publish.py` | 对应预测文件存在 |
| "复盘 [path]" / "retro [path]" / "T+3d" | `scripts/retro.py` | 对应预测文件存在 |
| "状态" / "status" / "看看进度" | `scripts/status.py` | 任意时刻 |
| "升级rubric" / "bump" / "更新公式" | `scripts/bump.py` | 校准池 ≥ 最小样本数 |
| "种子选题" / "seed" / "我有个想法" | `scripts/seed.py` | 任意时刻 |
| "读者画像" / "persona" / "我的读者是谁" | `scripts/persona.py` | 有已发文章 |
| "对标学习" / "learn" / "学一下 [source]" | `scripts/learn.py` | 有样本数据 |
| "迁移" / "migrate" / "更新schema" | `scripts/migrate.py` | schema 不是最新 |

## 项目目录结构

初始化后生成：

```
<content-project>/
├── .content-state.json        # 状态文件
├── .content-cache/            # 缓存
├── articles/                  # 成品稿
├── predictions/               # 盲预测记录（不可变）
├── scripts/                   # 草稿
├── samples/                   # 对标样本
├── pictures/                  # 配图
├── videos/                    # 视频素材
├── rubric_notes.md            # 评分规则
├── candidates.md              # 选题池
├── benchmark.md               # 对标基准
├── audience.md                # 读者画像
├── script_patterns.md         # 写作模式
```

## 脚本一览

| 脚本 | 功能 |
|------|------|
| `state.py` | 状态管理（读/写/初始化 .content-state.json） |
| `init.py` | 项目初始化 |
| `trends.py` | 多源热点采集 + 去重 + 粗打分 |
| `recommend.py` | 选题推荐 |
| `score.py` | rubric 打分 |
| `score_blind.py` | 盲打分（内部子代理） |
| `shoot.py` | 写稿助手 |
| `predict.py` | 盲预测 |
| `publish.py` | 发布记录 |
| `retro.py` | 复盘 |
| `status.py` | 状态面板 |
| `bump.py` | Rubric 升级 |
| `seed.py` | 种子选题 |
| `persona.py` | 读者画像 |
| `learn.py` | 对标学习 |
| `migrate.py` | Schema 迁移 |

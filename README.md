# Content Oracle / 内容先知

> 把每次"我感觉这条会爆"变成可校准的实验。
> Hermes Agent 内容创作校准系统

[![Version](https://img.shields.io/badge/version-0.2.0-orange)](CHANGELOG.md)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## 是什么

**Content Oracle** 是一套内容创作校准系统，把创作流程变成一个可衡量的预测循环：

> **抓热点 → 推荐选题 → 写稿 → 打分 → 盲预测 → 发布 → 复盘 → 进化 rubric**

受 [cheat-on-content](https://github.com/XBuilderLAB/cheat-on-content) 架构启发，专为 **Hermes Agent** 构建。14 个子技能覆盖创作全链路。

## 快速安装

### 前提

- 已安装 [Hermes Agent](https://hermes-agent.nousresearch.com)
- Python 3.8+

### 一键安装

```bash
# 方式一：克隆+安装（推荐）
git clone https://github.com/P-Jermy/content-oracle.git ~/content-oracle
cd ~/content-oracle
bash install.sh

# 方式二：直接用 Hermes 远程 skill 安装
# 在 Hermes 中说：
安装技能 content-oracle from https://github.com/P-Jermy/content-oracle
```

安装后，在你想做内容创作的目录中，对 Hermes 说：

```
初始化
```

### 手动安装

```bash
# 克隆
git clone https://github.com/P-Jermy/content-oracle.git ~/content-oracle

# symlink 到 Hermes skills 目录（实时更新用）
ln -sf ~/content-oracle ~/.hermes/skills/content-oracle

# 或 copy（冻结版本用）
cp -R ~/content-oracle ~/.hermes/skills/content-oracle
```

### 验证安装

在 Hermes 中说：

```
状态
```

如果看到状态面板输出，说明安装成功。

## 首次使用

```bash
# 1. 创建内容项目目录
mkdir my-content-project
cd my-content-project

# 2. 在 Hermes 中初始化
初始化

# 3. 开始创作循环
抓热点         # 采集今日趋势
推荐选题       # 从趋势+候选池推荐
写稿           # 开始写稿
盲预测         # 预测表现
发布           # 登记发布
复盘           # T+N 复盘
状态           # 查看当前看板
```

## 子技能一览

| 子技能 | 触发词 | 功能 |
|--------|--------|------|
| **content-init** | 初始化 / init | 创建项目目录结构 + state |
| **content-trends** | 抓热点 / trends | 多源热点采集（GitHub/HN/36氪） |
| **content-recommend** | 推荐选题 / recommend | 从候选池+趋势推荐 |
| **content-score** | 打分本篇 / score | 按 rubric 9 维评分 |
| **content-shoot** | 写稿 / shoot | 写稿助手，从候选生成草稿 |
| **content-predict** | 盲预测 / predict | 创建不可变盲预测记录 |
| **content-publish** | 发布 / publish | 登记发布信息 |
| **content-retro** | 复盘 / retro | T+N 复盘对比预测 |
| **content-status** | 状态 / status | 项目状态面板 |
| **content-bump** | 升级rubric / bump | Rubric 权重/桶升级 |
| **content-seed** | 种子选题 / seed | 基于兴趣生成选题 |
| **content-persona** | 读者画像 / persona | 从已发文章提取读者画像 |
| **content-learn** | 对标学习 / learn | 分析竞品样本提取模式 |
| **content-migrate** | 迁移 / migrate | Schema 版本迁移 |

详情见 [SKILL.md](SKILL.md)。

## 项目结构

安装后在你的内容项目目录中：

```
my-content-project/
├── .content-state.json        # 状态文件（不要手动编辑）
├── .content-cache/            # 趋势缓存
├── articles/                  # 成品稿
├── predictions/               # 盲预测记录（不可变）
├── scripts/                   # 草稿
├── samples/                   # 对标样本
├── pictures/                  # 配图
├── videos/                    # 视频素材
├── rubric_notes.md            # 评分规则
├── candidates.md              # 选题池
├── benchmark.md               # 对标基准
└── audience.md                # 读者画像
```

## 方法论三条不妥协原则

1. **盲预测**：预测必须在看到数据**之前**写完，一旦写完不可修改
2. **升级 = 全量重打**：rubric 升级时用新公式重判所有历史样本
3. **rubric 是工作台不是博物馆**：过时的观察删掉，不保留考古层

## 与 cheat-on-content 的区别

| | cheat-on-content | content-oracle |
|---|---|---|
| 目标 Agent | Claude Code / Codex | **Hermes Agent** |
| 安装方式 | CC skills symlink | Hermes skill symlink |
| 触发方式 | `/cheat-xxx` slash command | 自然语言指令 |
| 技术栈 | Bash hooks + CC harness | Python CLI + Hermes router |
| 内容形态 | 观点视频为主 | 通用（文章/视频/播客/thread） |

## 依赖

- Python 3.8+（仅标准库，无第三方依赖）
- 网络：GitHub Trending / HN Algolia API / 36氪 RSS

## License

MIT

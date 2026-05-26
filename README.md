<h1 align="center">
  Content Oracle / 内容先知
</h1>

<p align="center">
把每次"我感觉这条会爆"变成可校准的实验。
</p>

<p align="center">
<a href="CHANGELOG.md"><img src="https://img.shields.io/badge/version-0.1.0-orange" alt="Version"></a>
&nbsp;
<a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License"></a>
</p>

---

## 是什么

**Content Oracle** 是一套内容创作校准系统，受 [cheat-on-content](https://github.com/XBuilderLAB/cheat-on-content) 启发，专为 **Hermes Agent** 构建。

它把内容创作流程变成一个可衡量的预测循环：

> **打分 → 盲预测 → 发布 → 复盘 → 进化 rubric**

## 为什么

大部分创作者陷入同一个循环：
> 发布 → 数据出来 → 学不到东西 → 下一次继续赌

跑过 200 条的博主跟跑过 1 条的差距不到 10%——因为没在每次赌局后**记账**。

Content Oracle 让每一次判断都被记录、被复盘、被吸收进下一次的判断公式。

## 怎么用

### 安装

```bash
git clone https://github.com/P-Jermy/content-oracle.git
cd content-oracle
bash install.sh          # symlink 安装（推荐，用于实时更新）
# 或
bash install.sh --copy   # 冻结版本
```

### 初始化项目

```bash
cd my-content-project
# 在 Hermes 中说：
初始化
```

或者：

```bash
python3 scripts/init.py /path/to/my-project
```

### 日常使用

在 Hermes 中说：

| 你说 | 效果 |
|------|------|
| "抓热点" | 采集 GitHub Trending + HN 热点 |
| "推荐选题" | 从候选池+趋势推荐选题 |
| "打分这篇 path/to/draft.md" | 按 rubric 打分 |
| "盲预测 path/to/draft.md" | 创建不可变预测记录 |
| "已发布 predictions/xxx.md" | 登记发布 |
| "复盘 predictions/xxx.md" | 复盘准备 |
| "状态" | 查看项目看板 |

### 方法论

三条不妥协原则（详见 [shared-references/blind-prediction-protocol.md](shared-references/blind-prediction-protocol.md)）：

1. **盲预测**：预测必须在看到数据**之前**写完，不可修改
2. **升级 = 全量重打**：rubric 升级时用新公式重判所有历史样本
3. **rubric 是工作台不是博物馆**：过时的观察删掉

## 项目结构

```
content-oracle/
├── SKILL.md                    # Hermes 技能入口
├── scripts/                    # Python 核心脚本
│   ├── init.py                 # 项目初始化
│   ├── trends.py               # 热点采集
│   ├── recommend.py            # 选题推荐
│   ├── score.py                # rubric 打分
│   ├── predict.py              # 盲预测
│   └── publish.py              # 发布/复盘/状态
├── templates/                  # markdown 模板
├── shared-references/          # 协议文档
├── install.sh                  # 安装脚本
├── uninstall.sh                # 卸载脚本
└── CHANGELOG.md                # 更新日志
```

## 与 cheat-on-content 的区别

| | cheat-on-content | content-oracle |
|---|---|---|
| 目标 Agent | Claude Code / Codex | **Hermes Agent** |
| 安装方式 | CC skills symlink | Hermes skill |
| 触发方式 | `/cheat-xxx` slash command | 自然语言指令 |
| 技术栈 | Bash hooks + CC harness | Python CLI + Hermes |
| 内容形态 | 观点视频为主 | 通用（文章/视频/播客/thread） |

## License

MIT

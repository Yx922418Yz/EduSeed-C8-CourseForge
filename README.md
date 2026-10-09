# EduSeed-C8-CourseForge

> C8 · Project C「课程生产体系」——最小可运行原型（Proof of Capability）。
> 作者：李亚轩（Yx922418Yz），郑州西亚斯学院 软件工程 2025 级。

## 这是什么

一条课程生产流水线的**前两段最小实现**：

```
syllabus.md (教学大纲)
   │  courseforge.py 解析
   ▼
course_content_framework.json   （课程内容框架：周次/主题/目标/概念/周末交付物）
   │  实例化
   ▼
ilt_tasks.json                  （每周 ILT 讲师引导式培训任务骨架：引导话术/学员任务/成功标准/记忆检查点）
```

对应 Project C 的工作流：**Syllabus → Content → Agent(ILT)**。本原型先打通"大纲 → 结构化内容 → ILT 任务"这一段，验证流水线思路成立。

## 目录结构

```
EduSeed-C8-CourseForge/
├── src/
│   └── courseforge.py        # 核心脚本：syllabus.md -> 两个 JSON
├── samples/
│   ├── syllabus.md           # 输入样例（8 周 Python 入门到 AI 小项目大纲）
│   ├── course_content_framework.json   # 真实生成的输出样例 1
│   └── ilt_tasks.json                  # 真实生成的输出样例 2
├── LiYaxuan_C8_proposal.md   # C8 项目申请书（5 部分）
├── LiYaxuan_C8_AI日志.md
├── LiYaxuan_C8_拿来说明.md
└── README.md
```

## 怎么跑（本机已实测通过）

环境：Windows，Python 3.x（无需第三方依赖，只用标准库）。

```bash
# 1. 进入脚本目录
cd src

# 2. 用样例大纲跑一遍（输出到 samples/）
python courseforge.py ../samples/syllabus.md --outdir ../samples
```

预期输出：

```
[OK] 解析课程：Python 入门到 AI 小项目（8 周课程）
[OK] 共 8 个周次 / 8 个 ILT 任务
[OK] 写出：...\samples\course_content_framework.json
[OK] 写出：...\samples\ilt_tasks.json
```

## 换成你自己的大纲

只要把你的大纲写成下面这个格式，脚本就能解析：

```markdown
# 课程标题
> 一句简介

## 课程目标
- 目标一
- 目标二

## Week 1: 单元标题
### 学习目标
- 目标 A
- 目标 B
### 核心内容
- 内容点 1
- 内容点 2

## Week 2: ...
```

然后：

```bash
python courseforge.py 你的大纲.md --outdir 输出目录
```

## 当前边界（诚实说明）
- 这是**最小可运行原型**，不是完成品：大纲解析是基于 `## Week N:` 约定的轻量解析，暂不支持任意 Markdown。
- "周末交付物"目前是按周次映射的规则表 + 大纲标题，后续可换成大模型自动生成。
- 流水线后两段（ILT Agent 真正部署给学生用、学生作品自动归档作品集）尚未实现，是 Proposal 里 Week 3-8 的计划。

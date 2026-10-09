#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CourseForge —— Project C「课程生产体系」最小可运行原型
=====================================================
输入：一份教学大纲 syllabus.md
输出：
  1) course_content_framework.json  课程内容框架（周次/主题/目标/概念/交付物）
  2) ilt_tasks.json                 每周对应的 ILT（讲师引导式培训）任务骨架

设计理念（对应 C8 Project C 的 Syllabus -> Content -> Agent 流水线）：
  syllabus.md  --parse-->  内容框架 JSON  --instantiate-->  ILT 任务骨架 JSON
本脚本是流水线的"前两段"：从大纲自动产出可编排、可交给 Agent 的结构化内容。

用法：
  python courseforge.py <syllabus.md> [--outdir 输出目录]
默认：python courseforge.py ../samples/syllabus.md
"""

import argparse
import json
import os
import re
import sys
from datetime import date


# --------------------------------------------------------------------------- #
# 1. 解析 syllabus.md
# --------------------------------------------------------------------------- #
def parse_syllabus(md_text):
    """把 Markdown 大纲解析成结构化 dict。"""
    lines = md_text.splitlines()

    course_title = ""
    course_desc = ""
    goals = []
    units = []

    i = 0
    n = len(lines)
    while i < n:
        line = lines[i].rstrip()

        # 课程主标题
        if line.startswith("# ") and not course_title:
            course_title = line[2:].strip()
            i += 1
            continue

        # 引用块简介
        if line.startswith("> "):
            course_desc = line[2:].strip()
            i += 1
            continue

        # 课程目标
        if line.strip() == "## 课程目标":
            i += 1
            while i < n and not lines[i].startswith("## "):
                s = lines[i].strip()
                if s.startswith("- "):
                    goals.append(s[2:].strip())
                i += 1
            continue

        # 每一周：## Week N: 标题
        m = re.match(r"^##\s+Week\s+(\d+)\s*[:：]\s*(.+)$", line.strip())
        if m:
            week = int(m.group(1))
            unit_title = m.group(2).strip()
            objectives, topics = [], []
            i += 1
            # 读该周下面的 ### 小节
            while i < n and not lines[i].startswith("## "):
                sub = lines[i].strip()
                if sub.startswith("### 学习目标"):
                    i += 1
                    while i < n and not lines[i].startswith("### ") and not lines[i].startswith("## "):
                        s = lines[i].strip()
                        if s.startswith("- "):
                            objectives.append(s[2:].strip())
                        i += 1
                    continue
                if sub.startswith("### 核心内容"):
                    i += 1
                    while i < n and not lines[i].startswith("### ") and not lines[i].startswith("## "):
                        s = lines[i].strip()
                        if s.startswith("- "):
                            topics.append(s[2:].strip())
                        i += 1
                    continue
                i += 1
            units.append({
                "week": week,
                "title": unit_title,
                "objectives": objectives,
                "topics": topics,
            })
            continue

        i += 1

    return {
        "course_title": course_title,
        "course_desc": course_desc,
        "goals": goals,
        "units": units,
    }


# --------------------------------------------------------------------------- #
# 2. 内容框架 JSON
# --------------------------------------------------------------------------- #
def build_content_framework(parsed):
    units_out = []
    for u in parsed["units"]:
        # 由每周目标反推一个"周末交付物"
        deliverable = _derive_deliverable(u)
        units_out.append({
            "week": u["week"],
            "unit_title": u["title"],
            "learning_objectives": u["objectives"],
            "key_concepts": u["topics"],
            "weekend_deliverable": deliverable,
        })

    return {
        "meta": {
            "course_title": parsed["course_title"],
            "description": parsed["course_desc"],
            "total_weeks": len(parsed["units"]),
            "generated_on": str(date.today()),
            "generator": "CourseForge v0.1 (C8 Project C prototype)",
        },
        "course_goals": parsed["goals"],
        "units": units_out,
    }


def _derive_deliverable(unit):
    title = unit["title"]
    table = {
        1: "一个能在本机跑通的 hello 世界 + 一张你读懂的报错截图",
        2: "一个命令行小记事本（能读写本地 .txt）",
        3: "把任意 5 条个人笔记存成 memory.json 并能读回",
        4: "一张手绘/电子的「读记忆→提问→写记忆」循环图",
        5: "一段能拿到模型一句话回答的最小脚本",
        6: "一个能多轮对话、并记住上一轮内容的命令行小程序",
        7: "在对话里接入至少 1 个关键词触发的小工具",
        8: "整理好的开源仓库 + README + 一篇复盘",
    }
    return table.get(unit["week"], f"围绕《{title}》的一个可运行小作品")


# --------------------------------------------------------------------------- #
# 3. ILT（讲师引导式培训）任务骨架 JSON
# --------------------------------------------------------------------------- #
def build_ilt_tasks(frame):
    tasks = []
    for u in frame["units"]:
        week = u["week"]
        title = u["unit_title"]
        obj = u["learning_objectives"]
        concepts = u["key_concepts"]

        # 讲师引导脚本：把本周目标改写成"开场提问"
        opener = _build_opener(week, title, obj)

        task = {
            "task_id": f"ILT-W{week:02d}",
            "week": week,
            "title": f"Week {week} · {title}",
            "mode": "ILT",  # Interactive Learning Task，讲师引导式培训
            "estimated_minutes": 90,
            "instructor_guide": {
                "warmup_question": opener,
                "walkthrough_points": concepts,
                "common_pitfall": _pitfall(week),
            },
            "learner_task": {
                "input": f"完成本周《{title}》的动手练习，并产出：{u['weekend_deliverable']}",
                "starter_prompt_for_agent": (
                    f"你是我的学习搭子老师。现在是第 {week} 周，主题是《{title}》。"
                    f"我的学习目标是：{'；'.join(obj)}。"
                    f"请一步步引导我动手做，每步只给一个小任务，我做完再下一步。"
                ),
                "expected_output": u["weekend_deliverable"],
            },
            "success_criteria": [
                f"能口述本周目标：{obj[0] if obj else '（见大纲）'}",
                f"动手完成：{u['weekend_deliverable']}",
                "遇到报错时能自己先读懂报错再求助",
            ],
            "memory_checkpoint": (
                f"对话结束前，把'我这周搞懂了什么 / 还卡在哪'写进我的学习记忆文件，"
                f"下周开课时先读它。"
            ),
        }
        tasks.append(task)
    return {
        "meta": {
            "course_title": frame["meta"]["course_title"],
            "task_type": "ILT (Interactive Learning Task)",
            "total_tasks": len(tasks),
            "generated_on": str(date.today()),
        },
        "tasks": tasks,
    }


def _build_opener(week, title, objectives):
    if objectives:
        return (f"上一周我们搞定了上一步。这周进《{title}》——"
                f"我先问你：你觉得这周最该先搞懂的是哪一点？（提示：{objectives[0]}）")
    return f"这周我们来搞《{title}》，你打算先从哪儿下手？"


def _pitfall(week):
    pitfalls = {
        1: "环境装半天跑不起来就放弃——其实多半是路径/勾选问题。",
        2: "文件读写忘了关闭或编码，导致乱码。",
        3: "把 JSON 当 Python 字典直接写，忘记序列化。",
        4: "误以为大模型本身有记忆，关掉窗口还在。",
        5: "超时/密钥报错就卡住，不会读报错。",
        6: "每轮不注入历史，导致'失忆'。",
        7: "一上来追求全自动工具调用，把自己绕晕。",
        8: "README 写得太简略，别人看不懂怎么用。",
    }
    return pitfalls.get(week, "贪多嚼不烂，先跑通最小版本。")


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #
def main():
    ap = argparse.ArgumentParser(description="CourseForge: syllabus.md -> 课程框架 JSON + ILT 任务骨架")
    ap.add_argument("syllabus", help="输入 syllabus.md 路径")
    ap.add_argument("--outdir", default=None, help="输出目录（默认与 syllabus 同目录）")
    args = ap.parse_args()

    if not os.path.exists(args.syllabus):
        print(f"[ERROR] 找不到输入文件: {args.syllabus}", file=sys.stderr)
        sys.exit(1)

    with open(args.syllabus, "r", encoding="utf-8") as f:
        md = f.read()

    parsed = parse_syllabus(md)
    if not parsed["units"]:
        print("[ERROR] 没有解析到任何 Week，请检查 syllabus.md 是否用 '## Week N: 标题' 格式。",
              file=sys.stderr)
        sys.exit(2)

    outdir = args.outdir or os.path.dirname(os.path.abspath(args.syllabus))
    os.makedirs(outdir, exist_ok=True)

    framework = build_content_framework(parsed)
    ilt = build_ilt_tasks(framework)

    fp_framework = os.path.join(outdir, "course_content_framework.json")
    fp_ilt = os.path.join(outdir, "ilt_tasks.json")

    with open(fp_framework, "w", encoding="utf-8") as f:
        json.dump(framework, f, ensure_ascii=False, indent=2)
    with open(fp_ilt, "w", encoding="utf-8") as f:
        json.dump(ilt, f, ensure_ascii=False, indent=2)

    print(f"[OK] 解析课程：{parsed['course_title']}")
    print(f"[OK] 共 {len(parsed['units'])} 个周次 / {len(ilt['tasks'])} 个 ILT 任务")
    print(f"[OK] 写出：{fp_framework}")
    print(f"[OK] 写出：{fp_ilt}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Data preparation utilities for NumberTheory-Qwen.

Stage 1 smoke data is only used to verify the pipeline and is not a formal
baseline. Formal evaluation and training should focus on Number Theory only.

Supported modes:
- smoke_test: create a tiny local smoke-test jsonl file.
- inspect_public: inspect public dataset schemas and small samples.
"""

import argparse
import json
from collections import Counter
from itertools import islice
from pathlib import Path
from pprint import pformat

from datasets import get_dataset_config_names, get_dataset_split_names, load_dataset


SMOKE_OUTPUT_PATH = Path("data/processed/eval_small.jsonl")

SMOKE_SAMPLES = [
    {"id": "nt_001", "subject": "number_theory", "problem": "求 2025 除以 7 的余数。", "answer": "2"},
    {"id": "nt_002", "subject": "number_theory", "problem": "求 2^10 除以 7 的余数。", "answer": "2"},
    {"id": "nt_003", "subject": "number_theory", "problem": "求满足 x ≡ 2 (mod 5) 且 0 <= x < 20 的所有整数 x。", "answer": "2,7,12,17"},
    {"id": "nt_004", "subject": "number_theory", "problem": "求 gcd(84, 126)。", "answer": "42"},
    {"id": "nt_005", "subject": "number_theory", "problem": "求 lcm(12, 18)。", "answer": "36"},
    {"id": "nt_006", "subject": "number_theory", "problem": "判断 341 是否为质数。若不是，给出一个非平凡因数分解。", "answer": "11*31"},
    {"id": "nt_007", "subject": "number_theory", "problem": "求 5^3 除以 13 的余数。", "answer": "8"},
    {"id": "nt_008", "subject": "number_theory", "problem": "求最小正整数 n，使得 n 同时被 6 和 15 整除。", "answer": "30"},
    {"id": "nt_009", "subject": "number_theory", "problem": "求 1+2+...+100 除以 9 的余数。", "answer": "1"},
    {"id": "nt_010", "subject": "number_theory", "problem": "若整数 n 满足 n ≡ 3 (mod 4)，求 n^2 除以 8 的余数。", "answer": "1"},
]

DATASET_GROUPS = {
    "Omni-MATH-Rule": [
        "KbsdJames/Omni-MATH-Rule",
        "KbsdJames/Omni-MATH",
        "Omni-MATH/Omni-MATH",
    ],
    "Omni-MATH": [
        "KbsdJames/Omni-MATH",
        "Omni-MATH/Omni-MATH",
    ],
    "NuminaMath-1.5": [
        "AI-MO/NuminaMath-1.5",
    ],
    "NuminaMath-CoT": [
        "AI-MO/NuminaMath-CoT",
    ],
}

FIELD_CANDIDATES = {
    "problem/question": ["problem", "question", "prompt", "input"],
    "answer/final_answer": ["answer", "final_answer", "expected_answer", "target"],
    "solution": ["solution", "rationale", "reasoning", "cot"],
    "subject/domain/category/problem_type": ["subject", "domain", "category", "topic", "type", "problem_type"],
    "difficulty": ["difficulty", "level"],
}


def write_smoke_test() -> None:
    SMOKE_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with SMOKE_OUTPUT_PATH.open("w", encoding="utf-8") as f:
        for item in SMOKE_SAMPLES:
            row = dict(item)
            row["source"] = "manual_smoke_test"
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    counts = Counter(item["subject"] for item in SMOKE_SAMPLES)
    print(f"Saved smoke test data to: {SMOKE_OUTPUT_PATH}")
    print(f"Total samples: {len(SMOKE_SAMPLES)}")
    print(f"Number theory samples: {counts['number_theory']}")
    print("Note: this file is only a smoke test and is not a formal baseline.")


def inspect_repo(repo_id: str):
    lines = [f"- Repo: `{repo_id}`"]
    try:
        try:
            configs = get_dataset_config_names(repo_id)
        except Exception:
            configs = [None]

        lines.append(f"- Available configs: `{configs[:10]}`")
        config = configs[0] if configs and configs[0] not in [None, "default"] else None

        try:
            splits = get_dataset_split_names(repo_id, config) if config else get_dataset_split_names(repo_id)
        except Exception:
            splits = ["train"]

        lines.append(f"- Available splits: `{splits}`")
        split = splits[0]

        if config:
            ds = load_dataset(repo_id, config, split=split, streaming=True)
        else:
            ds = load_dataset(repo_id, split=split, streaming=True)
        rows = list(islice(ds, 2))

        if not rows:
            lines.append("- Status: loaded, but no sample rows found")
            return True, "\n".join(lines)

        columns = list(rows[0].keys())
        lines.append(f"- Column names: `{columns}`")

        for name, candidates in FIELD_CANDIDATES.items():
            found = [c for c in candidates if c in columns]
            lines.append(f"- {name} fields: `{found}`")

        text = pformat(rows, width=120).lower()
        number_theory_signal = any(
            key in text
            for key in ["number theory", "number_theory", "数论", "modulo", "congruence", "divisibility", "gcd"]
        )
        proof_signal = any(key in text for key in ["prove", "proof", "show that", "证明"])
        image_signal = any(key in text for key in ["image", "diagram", "figure", "如图", "图片"])

        lines.append(f"- Can filter Number Theory: `{number_theory_signal}`")
        lines.append(f"- Has proof/open-ended signals: `{proof_signal}`")
        lines.append(f"- Has image/diagram signals: `{image_signal}`")
        lines.append("- Suitable for formal eval: only if Number Theory + pure text + short answer + rule-verifiable")
        lines.append("- Suitable for training: yes if problem/question and solution/answer fields are available")
        lines.append("")
        lines.append("Sample rows:")
        for i, row in enumerate(rows, 1):
            lines.append(f"\nSample {i}:")
            lines.append("```text")
            lines.append(pformat(row, width=120))
            lines.append("```")

        return True, "\n".join(lines)
    except Exception as exc:
        lines.append("- Status: failed")
        lines.append(f"- Reason: `{type(exc).__name__}: {exc}`")
        return False, "\n".join(lines)


def inspect_public() -> None:
    Path("results").mkdir(exist_ok=True)
    out = [
        "# Public Dataset Inspection",
        "",
        "本报告用于 Stage 2：评分协议与公开数据集字段检查。",
        "",
        "目标：检查 Omni-MATH-Rule / Omni-MATH / NuminaMath-1.5 / NuminaMath-CoT 的字段结构，只加载少量样本，不保存原始数据。",
        "",
        "正式评测只使用纯文本、短答案、可自动评分的 Number Theory 题。",
        "",
    ]

    for group, repos in DATASET_GROUPS.items():
        out.append(f"## {group}")
        loaded = False
        for repo in repos:
            ok, report = inspect_repo(repo)
            out.append(report)
            out.append("")
            if ok:
                loaded = True
                break
        if not loaded:
            out.append("所有候选 repo 均未成功加载，需要后续人工确认 Hugging Face 数据集名称。")
            out.append("")

    Path("results/public_dataset_inspect.md").write_text("\n".join(out), encoding="utf-8")
    print("Wrote results/public_dataset_inspect.md")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["smoke_test", "inspect_public"], default="smoke_test")
    args = parser.parse_args()

    if args.mode == "smoke_test":
        write_smoke_test()
    elif args.mode == "inspect_public":
        inspect_public()


if __name__ == "__main__":
    main()

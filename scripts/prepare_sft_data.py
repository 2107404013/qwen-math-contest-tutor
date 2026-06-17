import json
import random
from pathlib import Path
from collections import Counter

import yaml


SAMPLES = [
    {
        "id": "sft_alg_001",
        "subject": "algebra",
        "problem": "已知 x+y=8, xy=15, 求 x^2+y^2。",
        "answer": "34",
        "solution": "由 x^2+y^2=(x+y)^2-2xy，代入得 8^2-2×15=64-30=34。因此最终答案是 \\boxed{34}。"
    },
    {
        "id": "sft_alg_002",
        "subject": "algebra",
        "problem": "若 a+b=5, a^2+b^2=13, 求 ab。",
        "answer": "6",
        "solution": "由 (a+b)^2=a^2+b^2+2ab，得 25=13+2ab，所以 ab=6。因此最终答案是 \\boxed{6}。"
    },
    {
        "id": "sft_alg_003",
        "subject": "algebra",
        "problem": "解方程 x^2-7x+12=0。",
        "answer": "3,4",
        "solution": "因式分解得 x^2-7x+12=(x-3)(x-4)。所以 x=3 或 x=4。因此最终答案是 \\boxed{3,4}。"
    },
    {
        "id": "sft_alg_004",
        "subject": "algebra",
        "problem": "若 t+1/t=5，求 t^2+1/t^2。",
        "answer": "23",
        "solution": "两边平方得 t^2+2+1/t^2=25，所以 t^2+1/t^2=23。因此最终答案是 \\boxed{23}。"
    },
    {
        "id": "sft_alg_005",
        "subject": "algebra",
        "problem": "求多项式 x^2-6x+10 的最小值。",
        "answer": "1",
        "solution": "配方得 x^2-6x+10=(x-3)^2+1。平方项最小为 0，所以最小值为 1。因此最终答案是 \\boxed{1}。"
    },
    {
        "id": "sft_alg_006",
        "subject": "algebra",
        "problem": "若正数 x,y 满足 xy=25，求 x+y 的最小值。",
        "answer": "10",
        "solution": "由 AM-GM，x+y>=2√xy=10，当 x=y=5 时取等号。因此最终答案是 \\boxed{10}。"
    },
    {
        "id": "sft_nt_001",
        "subject": "number_theory",
        "problem": "求 2026 除以 7 的余数。",
        "answer": "3",
        "solution": "因为 7×289=2023，所以 2026=7×289+3，余数为 3。因此最终答案是 \\boxed{3}。"
    },
    {
        "id": "sft_nt_002",
        "subject": "number_theory",
        "problem": "求 2^12 除以 7 的余数。",
        "answer": "1",
        "solution": "2^3=8≡1 (mod 7)，所以 2^12=(2^3)^4≡1。因此最终答案是 \\boxed{1}。"
    },
    {
        "id": "sft_nt_003",
        "subject": "number_theory",
        "problem": "求 gcd(96, 144)。",
        "answer": "48",
        "solution": "144=96+48，96=2×48，所以最大公约数是 48。因此最终答案是 \\boxed{48}。"
    },
    {
        "id": "sft_nt_004",
        "subject": "number_theory",
        "problem": "求 lcm(16, 24)。",
        "answer": "48",
        "solution": "gcd(16,24)=8，所以 lcm(16,24)=16×24/8=48。因此最终答案是 \\boxed{48}。"
    },
    {
        "id": "sft_nt_005",
        "subject": "number_theory",
        "problem": "求方程 5x ≡ 1 (mod 11) 的最小正整数解。",
        "answer": "9",
        "solution": "因为 5×9=45≡1 (mod 11)，所以最小正整数解为 9。因此最终答案是 \\boxed{9}。"
    },
    {
        "id": "sft_nt_006",
        "subject": "number_theory",
        "problem": "判断 221 是否为质数。若不是，给出一个非平凡因数分解。",
        "answer": "13*17",
        "solution": "因为 221=13×17，所以 221 不是质数。因此最终答案是 \\boxed{13*17}。"
    },
]


def to_sft_item(item, system_prompt):
    user = f"题目：{item['problem']}\n请一步步推理，并将最终答案写在 \\boxed{{}} 中。"
    return {
        "id": item["id"],
        "subject": item["subject"],
        "source": "manual_seed_sft",
        "problem": item["problem"],
        "answer": item["answer"],
        "solution": item["solution"],
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user},
            {"role": "assistant", "content": item["solution"]},
        ],
    }


def write_jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main():
    with open("configs/data_prep.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    random.seed(int(cfg["seed"]))
    rows = [to_sft_item(x, cfg["system_prompt"]) for x in SAMPLES]
    random.shuffle(rows)

    split = max(1, int(len(rows) * float(cfg["train_ratio"])))
    train_rows = rows[:split]
    val_rows = rows[split:]

    train_path = Path(cfg["output_train_file"])
    val_path = Path(cfg["output_val_file"])
    summary_path = Path(cfg["summary_path"])
    report_path = Path(cfg["report_path"])

    write_jsonl(train_path, train_rows)
    write_jsonl(val_path, val_rows)

    subject_counts = Counter(row["subject"] for row in rows)
    train_counts = Counter(row["subject"] for row in train_rows)
    val_counts = Counter(row["subject"] for row in val_rows)

    summary = {
        "stage": "Stage 2 - SFT data preparation",
        "total": len(rows),
        "train_total": len(train_rows),
        "val_total": len(val_rows),
        "subject_counts": dict(subject_counts),
        "train_subject_counts": dict(train_counts),
        "val_subject_counts": dict(val_counts),
        "train_file": str(train_path),
        "val_file": str(val_path),
        "format": "jsonl with messages field",
        "note": "当前是小规模手工 seed SFT 数据，用于验证 Stage 3 LoRA SFT 流程。",
    }

    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    report = f"""# Stage 2 数据准备报告

本阶段构建了一个小规模高中竞赛代数与数论 SFT 种子数据集，用于后续 LoRA SFT 流程验证。

## 数据规模

- 总样本数：{summary['total']}
- 训练集：{summary['train_total']}
- 验证集：{summary['val_total']}
- 代数样本：{subject_counts.get('algebra', 0)}
- 数论样本：{subject_counts.get('number_theory', 0)}

## 数据格式

每条样本保存为 jsonl，包含 id、subject、problem、answer、solution 和 messages 字段。

messages 字段采用 chat instruction 格式，后续可直接用于 LoRA SFT。

## 输出文件

- {train_path}
- {val_path}

注意：data/processed/ 已被 .gitignore 忽略，不应提交到 GitHub。
"""
    report_path.write_text(report, encoding="utf-8")

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

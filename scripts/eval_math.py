import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

import yaml
import torch
from sympy import simplify
from sympy.parsing.sympy_parser import parse_expr
from transformers import AutoModelForCausalLM, AutoTokenizer


def load_jsonl(path):
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def extract_boxed_answer(text):
    matches = re.findall(r"\\boxed\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}", text)
    if matches:
        return matches[-1].strip()

    patterns = [
        r"最终答案[:：]\s*([^\n。]+)",
        r"答案[:：]\s*([^\n。]+)",
        r"所以.*?为\s*([^\n。]+)",
    ]
    for pattern in patterns:
        found = re.findall(pattern, text)
        if found:
            return found[-1].strip()
    return ""


def normalize_answer(ans):
    if ans is None:
        return ""
    ans = str(ans).strip().lower()
    replacements = {
        "，": ",", "。": "", "；": ";", "：": ":",
        "（": "(", "）": ")", "×": "*", "·": "*",
        "\\cdot": "*", "\\times": "*", "−": "-",
        "\\left": "", "\\right": "", "\\,": "",
        "$": "", " ": "", "\n": "",
    }
    for old, new in replacements.items():
        ans = ans.replace(old, new)
    ans = ans.replace("{", "").replace("}", "")
    return ans


def split_items(ans):
    ans = normalize_answer(ans)
    if not ans:
        return []
    return [x for x in re.split(r"[,;，；、]", ans) if x]


def sympy_equal(a, b):
    try:
        a = normalize_answer(a).replace("^", "**")
        b = normalize_answer(b).replace("^", "**")
        return simplify(parse_expr(a) - parse_expr(b)) == 0
    except Exception:
        return False


def is_equiv(pred, gold):
    pred_n = normalize_answer(pred)
    gold_n = normalize_answer(gold)
    if pred_n == gold_n:
        return True

    pred_items = split_items(pred)
    gold_items = split_items(gold)
    if pred_items and gold_items and sorted(pred_items) == sorted(gold_items):
        return True

    if sympy_equal(pred, gold):
        return True

    if pred_items and gold_items and len(pred_items) == len(gold_items):
        used = [False] * len(gold_items)
        for p in pred_items:
            ok = False
            for i, g in enumerate(gold_items):
                if not used[i] and (normalize_answer(p) == normalize_answer(g) or sympy_equal(p, g)):
                    used[i] = True
                    ok = True
                    break
            if not ok:
                return False
        return True

    return False


def build_prompt(tokenizer, template, problem):
    user_prompt = template.replace("{problem}", problem)
    messages = [
        {"role": "system", "content": "你是一名严谨的高中数学竞赛辅导老师，擅长代数与数论。"},
        {"role": "user", "content": user_prompt},
    ]
    try:
        return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    except Exception:
        return user_prompt


def summarize(results):
    by_subject = defaultdict(lambda: {"total": 0, "correct": 0})
    correct = 0

    for row in results:
        subject = row["subject"]
        by_subject[subject]["total"] += 1
        if row["is_correct"]:
            correct += 1
            by_subject[subject]["correct"] += 1

    total = len(results)

    def acc(c, t):
        return round(c / t, 4) if t else 0.0

    return {
        "total": total,
        "correct": correct,
        "accuracy": acc(correct, total),
        "algebra_total": by_subject["algebra"]["total"],
        "algebra_correct": by_subject["algebra"]["correct"],
        "algebra_accuracy": acc(by_subject["algebra"]["correct"], by_subject["algebra"]["total"]),
        "number_theory_total": by_subject["number_theory"]["total"],
        "number_theory_correct": by_subject["number_theory"]["correct"],
        "number_theory_accuracy": acc(by_subject["number_theory"]["correct"], by_subject["number_theory"]["total"]),
    }


def classify_error(row):
    if not row.get("pred_answer"):
        return "最终答案格式错误"
    if len(row.get("model_output", "")) > 1800:
        return "推理过程过长或跑偏"
    if row["subject"] == "algebra":
        return "代数变形错误"
    return "数论同余/整除错误"


def write_error_analysis(results, summary, path):
    wrong = [r for r in results if not r["is_correct"]]
    groups = defaultdict(int)
    for row in wrong:
        groups[classify_error(row)] += 1

    cases = wrong[:5]
    lines = [
        "# Baseline Error Analysis",
        "",
        "## Summary",
        "",
        f"- Total: {summary['total']}",
        f"- Correct: {summary['correct']}",
        f"- Accuracy: {summary['accuracy']}",
        f"- Algebra accuracy: {summary['algebra_accuracy']}",
        f"- Number theory accuracy: {summary['number_theory_accuracy']}",
        "",
        "## Main Error Types",
        "",
        f"- 代数变形错误: {groups['代数变形错误']}",
        f"- 数论同余/整除错误: {groups['数论同余/整除错误']}",
        f"- 最终答案格式错误: {groups['最终答案格式错误']}",
        f"- 推理过程过长或跑偏: {groups['推理过程过长或跑偏']}",
        "",
        "## Typical Error Cases",
        "",
    ]

    if not cases:
        lines.append("No wrong cases found in this small baseline run.")
    else:
        for idx, row in enumerate(cases, 1):
            lines.extend([
                f"### Case {idx}: {row['id']}",
                "",
                f"- Subject: {row['subject']}",
                f"- Problem: {row['problem']}",
                f"- Gold answer: `{row['gold_answer']}`",
                f"- Pred answer: `{row.get('pred_answer', '')}`",
                f"- Possible reason: {classify_error(row)}",
                "",
            ])

    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/baseline_eval.yaml")
    args = parser.parse_args()

    with open(args.config, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is not available. Please run on the remote RTX4090 server.")

    samples = load_jsonl(cfg["eval_file"])
    target_subjects = set(cfg.get("target_subjects", []))
    if target_subjects:
        samples = [x for x in samples if x["subject"] in target_subjects]
    samples = samples[: int(cfg.get("max_eval_samples", len(samples)))]

    model_name = cfg["model_name"]
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        trust_remote_code=True,
        low_cpu_mem_usage=True,
    )
    model.eval()

    results = []
    for i, item in enumerate(samples, 1):
        print(f"[{i}/{len(samples)}] {item['id']}")

        prompt = build_prompt(tokenizer, cfg["prompt_template"], item["problem"])
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=int(cfg.get("max_new_tokens", 1024)),
                do_sample=bool(cfg.get("do_sample", False)),
                temperature=float(cfg.get("temperature", 0.0)) if cfg.get("do_sample", False) else None,
                top_p=float(cfg.get("top_p", 1.0)),
                pad_token_id=tokenizer.eos_token_id,
            )

        generated = outputs[0][inputs["input_ids"].shape[-1]:]
        model_output = tokenizer.decode(generated, skip_special_tokens=True).strip()
        pred = extract_boxed_answer(model_output)
        correct = is_equiv(pred, item["answer"])

        results.append({
            "id": item["id"],
            "subject": item["subject"],
            "problem": item["problem"],
            "gold_answer": item["answer"],
            "model_output": model_output,
            "pred_answer": pred,
            "is_correct": correct,
        })

    output_path = Path(cfg["output_path"])
    summary_path = Path(cfg["summary_path"])
    error_path = Path(cfg.get("error_analysis_path", "results/error_analysis.md"))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    summary = summarize(results)
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    write_error_analysis(results, summary, error_path)

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"Saved: {output_path}")
    print(f"Saved: {summary_path}")
    print(f"Saved: {error_path}")


if __name__ == "__main__":
    main()

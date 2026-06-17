#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Evaluator utilities for NumberTheory-Qwen.

Primary scorer: Math-Verify final-answer equivalence.
Fallback scorers: normalization, list-answer matching, equation RHS extraction,
and simple SymPy equivalence.

Main metric: Final Answer Accuracy.
Auxiliary metrics: Boxed Answer Rate, Extraction Success Rate, and Error Type Distribution.
"""

import argparse
import json
import re
import unicodedata
from pathlib import Path

try:
    from math_verify import parse, verify

    MATH_VERIFY_AVAILABLE = True
except Exception:
    parse = None
    verify = None
    MATH_VERIFY_AVAILABLE = False

try:
    import sympy as sp
except Exception:
    sp = None


def extract_boxed_answer(text):
    if not text:
        return None
    matches = re.findall(r"\\boxed\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}", text)
    return matches[-1].strip() if matches else None


def extract_answer_candidates(text):
    if not text:
        return []

    candidates = []
    boxed = extract_boxed_answer(text)
    if boxed:
        candidates.append(boxed)

    patterns = [
        r"最终答案(?:是|为)?[:：]?\s*([^\n。；;]+)",
        r"答案(?:是|为)?[:：]?\s*([^\n。；;]+)",
        r"因此[:：]?\s*([^\n。；;]+)",
        r"所以[:：]?\s*([^\n。；;]+)",
    ]
    for pattern in patterns:
        candidates.extend(item.strip() for item in re.findall(pattern, str(text)))

    candidates.append(str(text).strip())

    extra = []
    for candidate in candidates:
        if "=" in candidate:
            extra.append(candidate.split("=")[-1].strip())
    candidates.extend(extra)

    deduped = []
    seen = set()
    for candidate in candidates:
        if candidate and candidate not in seen:
            deduped.append(candidate)
            seen.add(candidate)
    return deduped


def latex_frac_to_slash(ans):
    return re.sub(r"\\frac\s*\{([^{}]+)\}\s*\{([^{}]+)\}", r"\1/\2", ans)


def normalize_answer(ans):
    if ans is None:
        return ""

    ans = unicodedata.normalize("NFKC", str(ans))
    ans = latex_frac_to_slash(ans)
    ans = ans.strip()

    ans = ans.replace("$", "")
    ans = ans.replace("\\left", "").replace("\\right", "")
    ans = ans.replace("\\,", "").replace("\\;", "").replace("\\!", "")
    ans = re.sub(r"\\text\s*\{([^{}]*)\}", r"\1", ans)

    ans = ans.replace("，", ",").replace("；", ",").replace("、", ",")
    ans = ans.replace("。", "").replace(".", "")
    ans = ans.replace(" 或 ", ",").replace(" 和 ", ",")
    ans = ans.replace("或", ",").replace("和", ",")

    ans = re.sub(r"\b[a-zA-Z]\s*=", "", ans)
    ans = ans.replace("{", "").replace("}", "")
    ans = ans.replace(" ", "")
    ans = ans.strip(",;:：")
    return ans


def split_list_answer(ans):
    norm = normalize_answer(ans)
    if "," not in norm:
        return None
    parts = [part for part in norm.split(",") if part]
    return sorted(parts) if parts else None


def verify_with_math_verify(pred, gold):
    if not MATH_VERIFY_AVAILABLE:
        return False, "math_verify_unavailable"
    try:
        return bool(verify(parse(gold), parse(pred))), "math_verify"
    except Exception as exc:
        return False, f"math_verify_error:{type(exc).__name__}"


def sympy_equiv(pred, gold):
    if sp is None:
        return False
    try:
        pred_expr = normalize_answer(pred).replace("^", "**")
        gold_expr = normalize_answer(gold).replace("^", "**")
        return bool(sp.simplify(sp.sympify(pred_expr) - sp.sympify(gold_expr)) == 0)
    except Exception:
        return False


def is_equiv(pred, gold):
    candidates = extract_answer_candidates(pred)
    gold_norm = normalize_answer(gold)

    for candidate in candidates:
        candidate_norm = normalize_answer(candidate)

        ok, method = verify_with_math_verify(candidate, gold)
        if ok:
            return True, method, candidate, candidate_norm, gold_norm

        if candidate_norm == gold_norm:
            return True, "normalized_exact", candidate, candidate_norm, gold_norm

        pred_list = split_list_answer(candidate)
        gold_list = split_list_answer(gold)
        if pred_list is not None and gold_list is not None and pred_list == gold_list:
            return True, "list_equiv", candidate, candidate_norm, gold_norm

        if "=" in candidate:
            rhs = candidate.split("=")[-1].strip()
            rhs_norm = normalize_answer(rhs)
            if rhs_norm == gold_norm:
                return True, "equation_rhs", rhs, rhs_norm, gold_norm

        if sympy_equiv(candidate, gold):
            return True, "sympy_equiv", candidate, candidate_norm, gold_norm

    raw = candidates[0] if candidates else ""
    return False, "no_match", raw, normalize_answer(raw), gold_norm


def classify_gold_answer(problem, gold):
    if not gold or not str(gold).strip():
        return "empty_answer"

    text = f"{problem}\n{gold}".lower()
    if any(key in text for key in ["image", "diagram", "figure", "如图", "图片"]):
        return "possible_image_problem"
    if any(key in text for key in ["prove", "proof", "show that", "证明"]):
        return "possible_proof"
    if len(str(gold)) > 120:
        return "long_solution_like_answer"
    if any(key in str(gold).lower() for key in ["open", "not unique", "不唯一", "无法确定"]):
        return "unsupported_format"

    return "short_answer"


def classify_eval_case(pred, gold, model_output="", problem=""):
    gold_type = classify_gold_answer(problem, gold)
    if gold_type != "short_answer":
        return "unsuitable_for_rule_eval"

    ok, _, _, _, _ = is_equiv(pred, gold)
    if ok:
        return "correct"

    if model_output and "\\boxed" not in model_output:
        return "format_error"

    return "model_error"


def run_evaluator_tests():
    tests = [
        {"pred": "2 和 3", "gold": "2,3", "expected": True},
        {"pred": "{2,3}", "gold": "2,3", "expected": True},
        {"pred": "x=2 或 x=3", "gold": "2,3", "expected": True},
        {"pred": r"\frac{1}{2}", "gold": "1/2", "expected": True},
        {"pred": "0.5", "gold": "1/2", "expected": True},
        {"pred": "x^3+y^3+z^3=3xyz", "gold": "3xyz", "expected": True},
        {"pred": "1", "gold": "6", "expected": False},
        {"pred": "12", "gold": "12", "expected": True},
        {"pred": "-1", "gold": "1", "expected": False},
        {"pred": "n is even", "gold": "偶数", "expected": False},
    ]

    results = []
    all_passed = True

    for idx, item in enumerate(tests, 1):
        got, method, raw_pred, norm_pred, norm_gold = is_equiv(item["pred"], item["gold"])
        passed = got == item["expected"]
        all_passed = all_passed and passed
        results.append(
            {
                "id": idx,
                "pred": item["pred"],
                "gold": item["gold"],
                "expected": item["expected"],
                "got": got,
                "passed": passed,
                "match_method": method,
                "raw_pred_answer": raw_pred,
                "normalized_pred": norm_pred,
                "normalized_gold": norm_gold,
            }
        )

    output = {
        "math_verify_available": MATH_VERIFY_AVAILABLE,
        "all_passed": all_passed,
        "tests": results,
    }

    Path("results").mkdir(exist_ok=True)
    Path("results/evaluator_test.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(output, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test_evaluator", action="store_true")
    args = parser.parse_args()

    if args.test_evaluator:
        run_evaluator_tests()
        return

    raise SystemExit("Stage 2 only supports --test_evaluator. Model inference is disabled in this stage.")


if __name__ == "__main__":
    main()

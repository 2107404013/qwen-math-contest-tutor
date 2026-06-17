import json
from pathlib import Path
from collections import Counter

OUTPUT_PATH = Path("data/processed/eval_small.jsonl")

SAMPLES = [
    {"id": "alg_001", "subject": "algebra", "problem": "若 x+y=6, xy=5, 求 x^2+y^2 的值。", "answer": "26"},
    {"id": "alg_002", "subject": "algebra", "problem": "已知 a+b=3, a^2+b^2=5, 求 ab。", "answer": "2"},
    {"id": "alg_003", "subject": "algebra", "problem": "若 x^2-5x+6=0, 求所有 x 的值。", "answer": "2,3"},
    {"id": "alg_004", "subject": "algebra", "problem": "化简 (x-1)(x+1)-x(x-2)。", "answer": "2x-1"},
    {"id": "alg_005", "subject": "algebra", "problem": "若 t+1/t=4, 求 t^2+1/t^2 的值。", "answer": "14"},
    {"id": "alg_006", "subject": "algebra", "problem": "已知 x^2+1/x^2=7, 求 (x+1/x)^2 的可能值。", "answer": "9"},
    {"id": "alg_007", "subject": "algebra", "problem": "若 a-b=2, ab=3, 求 a^2+b^2。", "answer": "10"},
    {"id": "alg_008", "subject": "algebra", "problem": "方程 x^2-4x+k=0 有两个相等实根, 求 k。", "answer": "4"},
    {"id": "alg_009", "subject": "algebra", "problem": "若 m+n=1, mn=-6, 求 m^3+n^3。", "answer": "19"},
    {"id": "alg_010", "subject": "algebra", "problem": "求多项式 x^2+6x+9 的最小值。", "answer": "0"},
    {"id": "alg_011", "subject": "algebra", "problem": "若正数 x,y 满足 xy=16, 求 x+y 的最小值。", "answer": "8"},
    {"id": "alg_012", "subject": "algebra", "problem": "已知 x+y+z=0, 求 x^3+y^3+z^3 与 xyz 的关系。", "answer": "3xyz"},
    {"id": "alg_013", "subject": "algebra", "problem": "若等差数列首项为 3, 公差为 2, 求第 10 项。", "answer": "21"},
    {"id": "alg_014", "subject": "algebra", "problem": "若 x^2-1=0, 求所有实数解。", "answer": "-1,1"},
    {"id": "alg_015", "subject": "algebra", "problem": "若 a^2-2a+1=0, 求 a。", "answer": "1"},

    {"id": "nt_001", "subject": "number_theory", "problem": "求 2025 除以 7 的余数。", "answer": "2"},
    {"id": "nt_002", "subject": "number_theory", "problem": "求 2^10 除以 7 的余数。", "answer": "2"},
    {"id": "nt_003", "subject": "number_theory", "problem": "求满足 x ≡ 2 (mod 5) 且 0 <= x < 20 的所有整数 x。", "answer": "2,7,12,17"},
    {"id": "nt_004", "subject": "number_theory", "problem": "求 gcd(84, 126)。", "answer": "42"},
    {"id": "nt_005", "subject": "number_theory", "problem": "求 lcm(12, 18)。", "answer": "36"},
    {"id": "nt_006", "subject": "number_theory", "problem": "判断 341 是否为质数。若不是, 给出一个非平凡因数分解。", "answer": "11*31"},
    {"id": "nt_007", "subject": "number_theory", "problem": "求 5^3 除以 13 的余数。", "answer": "8"},
    {"id": "nt_008", "subject": "number_theory", "problem": "求最小正整数 n, 使得 n 同时被 6 和 15 整除。", "answer": "30"},
    {"id": "nt_009", "subject": "number_theory", "problem": "求 1+2+...+100 除以 9 的余数。", "answer": "6"},
    {"id": "nt_010", "subject": "number_theory", "problem": "若整数 n 满足 n ≡ 3 (mod 4), 求 n^2 除以 8 的余数。", "answer": "1"},
    {"id": "nt_011", "subject": "number_theory", "problem": "求方程 3x ≡ 1 (mod 7) 的最小正整数解。", "answer": "5"},
    {"id": "nt_012", "subject": "number_theory", "problem": "求 100! 末尾有多少个 0。", "answer": "24"},
    {"id": "nt_013", "subject": "number_theory", "problem": "求 17 和 31 的最大公约数。", "answer": "1"},
    {"id": "nt_014", "subject": "number_theory", "problem": "求 3^4 除以 10 的余数。", "answer": "1"},
    {"id": "nt_015", "subject": "number_theory", "problem": "求最小正整数 x, 使 x ≡ 1 (mod 3) 且 x ≡ 2 (mod 5)。", "answer": "7"},
]

def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        for item in SAMPLES:
            item = dict(item)
            item["source"] = "manual_small_eval"
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    counts = Counter(item["subject"] for item in SAMPLES)
    print(f"Saved to: {OUTPUT_PATH}")
    print(f"Total samples: {len(SAMPLES)}")
    print(f"Algebra samples: {counts['algebra']}")
    print(f"Number theory samples: {counts['number_theory']}")

if __name__ == "__main__":
    main()

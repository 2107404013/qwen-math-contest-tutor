# Baseline Error Analysis

## Summary

- Total: 30
- Correct: 27
- Accuracy: 0.9
- Algebra accuracy: 0.8667
- Number theory accuracy: 0.9333

## Main Error Types

- 代数变形错误: 2
- 数论同余/整除错误: 1
- 最终答案格式错误: 0
- 推理过程过长或跑偏: 0

## Typical Error Cases

### Case 1: alg_003

- Subject: algebra
- Problem: 若 x^2-5x+6=0, 求所有 x 的值。
- Gold answer: `2,3`
- Pred answer: `2 \text{ 和 } 3`
- Possible reason: 代数变形错误

### Case 2: alg_012

- Subject: algebra
- Problem: 已知 x+y+z=0, 求 x^3+y^3+z^3 与 xyz 的关系。
- Gold answer: `3xyz`
- Pred answer: `x^3 + y^3 + z^3 = 3xyz`
- Possible reason: 代数变形错误

### Case 3: nt_009

- Subject: number_theory
- Problem: 求 1+2+...+100 除以 9 的余数。
- Gold answer: `6`
- Pred answer: `1`
- Possible reason: 数论同余/整除错误


# Qwen-Math-Contest-Tutor

Qwen-Math-Contest-Tutor is a lightweight math question-answering assistant project for high-school olympiad-style algebra and number theory.

The project is built around `Qwen/Qwen2.5-Math-1.5B-Instruct` as the student model and uses `Qwen/Qwen2.5-Math-7B-Instruct` as the preferred teacher model for answer distillation and optional white-box logits distillation.

## Project Goal

Build a compact, maintainable training and evaluation pipeline for a contest math tutor focused on:

- high-school olympiad algebra
- high-school olympiad number theory
- answer accuracy and boxed-answer accuracy
- reasoning format quality
- error-case analysis

## Model Choices

- Student model: `Qwen/Qwen2.5-Math-1.5B-Instruct`
- Teacher model: `Qwen/Qwen2.5-Math-7B-Instruct`
- Main training approach: LoRA SFT, teacher answer distillation, optional white-box logits distillation, and GRPO

## Training Stages

- Stage 0: Initialize project, environment, and context files
- Stage 1: Tokenizer alignment check and baseline evaluation
- Stage 2: Prepare algebra and number theory datasets
- Stage 3: LoRA SFT
- Stage 4: Teacher answer distillation
- Stage 5: Optional white-box logits distillation
- Stage 6: GRPO reinforcement learning fine-tuning
- Stage 7: Demo and README packaging

## File Structure

```text
Qwen-Math-Contest-Tutor/
  README.md
  CONTEXT.md
  requirements.txt
  .gitignore
  configs/
  scripts/
    check_env_tokenizer.py
  data/
    README.md
  results/
```

## Data And Artifact Policy

Do not upload model weights, checkpoints, raw datasets, processed datasets, Hugging Face cache files, or wandb artifacts to GitHub.

Training outputs should stay local under directories such as `outputs/`, `checkpoints/`, or `models/`. These paths are ignored by Git.

## Baseline Evaluation

本阶段评测原始 Qwen2.5-Math-1.5B-Instruct 在高中竞赛代数和数论小测试集上的表现，作为后续 LoRA SFT、教师蒸馏和 GRPO 的对比基线。

评测重点包括：
- answer accuracy
- boxed answer accuracy
- algebra accuracy
- number theory accuracy
- error analysis

首次 baseline 使用 `data/processed/eval_small.jsonl` 小规模样例集跑通流程，实际运行后会更新 `results/baseline_summary.json` 和 `results/error_analysis.md`。

## Stage 2：数据准备

本阶段构建高中竞赛代数与数论方向的 SFT 数据格式，输出训练集和验证集 jsonl 文件。每条样本包含题目、短答案、完整推理答案，以及可直接用于 chat-style SFT 的 `messages` 字段。

当前版本先使用小规模手工 seed 数据验证流程，后续会继续接入 NuminaMath、OlympiadBench 或自建竞赛题库，并筛选 algebra 与 number_theory 样本。

数据输出位于：

- `data/processed/sft_train.jsonl`
- `data/processed/sft_val.jsonl`

这些文件不提交到 GitHub，只在服务器本地保存。

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

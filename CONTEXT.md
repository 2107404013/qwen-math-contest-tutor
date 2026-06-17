# CONTEXT

## Project Goal

Build `Qwen-Math-Contest-Tutor`, a lightweight math question-answering assistant for high-school contest algebra and number theory.

## Hardware

Remote training server: 2 x RTX 4090. Scripts should prefer single-GPU runnable defaults and allow two-GPU acceleration.

## Base Model

`Qwen/Qwen2.5-Math-1.5B-Instruct`

## Teacher Model

`Qwen/Qwen2.5-Math-7B-Instruct`

## Target Domain

High-school olympiad-style algebra and number theory.

## Current Stage

Stage 0: Initialize project repository, environment files, and context tracking.

## Completed

- Confirmed the current directory is already a Git repository.
- Confirmed no `remote origin` is configured yet.
- Created the minimal project skeleton.
- Added dependency list in `requirements.txt`.
- Added Git ignore rules for datasets, checkpoints, model files, caches, and local secrets.
- Added `scripts/check_env_tokenizer.py` for environment and tokenizer compatibility checks.
- Ran tokenizer/config alignment check and saved output to `results/tokenizer_check.txt`.

## Key Decisions

- Keep each stage small and commit only core files.
- Do not upload raw datasets, processed datasets, model weights, checkpoints, Hugging Face cache, or wandb artifacts.
- Only load tokenizer and config during Stage 0 checks; do not download model weights.
- Local Stage 0 check used a temporary Python environment with `transformers`; local `torch` was not installed, so GPU availability could not be checked on this machine.
- Student and teacher tokenizers have identical effective tokenizer vocabularies and encode the Chinese math test text identically.
- Student and teacher `config.vocab_size` values differ, so future white-box logits KL distillation must compute KL only over `common_vocab`.
- Stage 0 tokenizer result: `len(tokenizer) = 151665` for both models, student `config.vocab_size = 151936`, teacher `config.vocab_size = 152064`, `get_vocab equal = True`, `test encode equal = True`, `common_vocab = 151665`.

## Next Step

Provide a GitHub repository URL and add it as `origin`, then push the Stage 0 commit. After that, Stage 1 can add tokenizer alignment report polishing and baseline evaluation for a small algebra/number-theory test set.

## Git Rule

At the end of each stage, update `CONTEXT.md`, run status checks, stage the intended files, commit, and push to GitHub. If `origin` is missing or push fails, report the failure once and ask for the required GitHub remote or command.

## Execution Rule

All training, evaluation, model downloading, Hugging Face cache, data preprocessing, checkpoint saving, and git operations must be executed on the remote 2×RTX4090 server. Local Windows is only used for VSCode Remote-SSH editing and connection. Do not run model inference or training locally.

## Stage 1 - 基线评测

Execution Rule:
All training, evaluation, model downloading, Hugging Face cache, data preprocessing, checkpoint saving, and git operations must be executed on the remote 2×RTX4090 server. Local Windows is only used for VSCode Remote-SSH editing and connection. Do not run model inference or training locally.

中文说明：所有训练、评测、模型下载、Hugging Face 缓存、数据处理、checkpoint 保存和 git 操作都必须在远端 2×RTX4090 服务器执行。本地 Windows 只用于 VSCode Remote-SSH 编辑和连接，不允许在本地运行模型推理或训练。

Current Stage: Stage 1 - Baseline Evaluation

执行环境：
- 远端 2×RTX4090 服务器
- Conda 环境：qwenmath
- 本地 Windows 仅用于 Remote-SSH 编辑

基线模型：
- Qwen/Qwen2.5-Math-1.5B-Instruct

评测领域：
- 高中竞赛代数
- 高中竞赛数论

Stage 1 核心文件：
- configs/baseline_eval.yaml
- scripts/prepare_data.py
- scripts/eval_math.py
- results/baseline_eval.json
- results/baseline_summary.json
- results/error_analysis.md

本阶段目标：
- 构造小规模代数与数论评测集
- 在不训练模型的情况下评测原始 1.5B 模型
- 输出逐题结果、总体准确率、分领域准确率和错误分析

下一步：
- 手动运行 scripts/prepare_data.py
- 手动运行 scripts/eval_math.py
- 查看 baseline_summary.json 和 error_analysis.md
- 从远端服务器 git commit 并 push


## Stage 1 运行结果

Baseline 评测已在远端服务器完成。

评测结果：
- total: 30
- correct: 27
- accuracy: 0.9
- algebra_accuracy: 0.8667
- number_theory_accuracy: 0.9333

主要错误类型已记录在 results/error_analysis.md。

下一阶段建议：
- Stage 2 准备更高质量的高中竞赛代数与数论训练数据
- 为 Stage 3 LoRA SFT 构造统一 instruction 数据格式


## Stage 2 - 数据准备

当前阶段：Stage 2 - 高中竞赛代数与数论 SFT 数据准备

已完成：
- 新增 configs/data_prep.yaml
- 新增 scripts/prepare_sft_data.py
- 生成本地训练集 data/processed/sft_train.jsonl
- 生成本地验证集 data/processed/sft_val.jsonl
- 生成 results/stage2_data_summary.json
- 生成 results/stage2_data_report.md

数据统计：
- 总样本数：12
- 训练集样本数：10
- 验证集样本数：2
- 代数样本数：6
- 数论样本数：6

关键决定：
- 当前先使用小规模手工 seed SFT 数据验证格式和流程。
- data/processed/ 不提交到 GitHub。
- 后续再接入更大规模公开数据集或自建竞赛题库。

下一步：
- Stage 3：基于 Qwen/Qwen2.5-Math-1.5B-Instruct 进行 LoRA SFT。
- 训练脚本应优先支持单卡 4090，可通过 accelerate 或 torchrun 支持双卡。

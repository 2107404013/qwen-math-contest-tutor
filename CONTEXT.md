# CONTEXT.md

## Project Name
NumberTheory-Qwen

## Project Goal
NumberTheory-Qwen：面向高中竞赛数论题的轻量级数学问答助手。

## Hardware
Remote 2x RTX4090 server.

## Student Model
Qwen/Qwen2.5-Math-1.5B-Instruct

## Teacher Model
Qwen/Qwen2.5-Math-7B-Instruct

## Target Domain
High-school olympiad number theory

## Current Stage
Stage 2 - Scoring Protocol and Dataset Inspection

## Formal Eval Size
200

## Training Data
NuminaMath-1.5 Number Theory, first 5k then 10k

## Prompt Language
Chinese

## Scoring
Math-Verify final-answer equivalence

## Stage 1 Status
Smoke test completed, not formal baseline.

Stage 1 的 30 题结果只用于验证 pipeline，包括数据读取、模型加载、生成、评分和结果保存流程。该结果不作为正式 baseline。正式 baseline 后续使用 `data/processed/public_number_theory_eval.jsonl`。

## Stage 2 Status
当前阶段只进行评分协议与公开数据集字段检查。

- 不训练模型；
- 不运行模型推理；
- 不下载 Qwen 模型权重；
- 检查 Omni-MATH-Rule / Omni-MATH / NuminaMath-1.5 / NuminaMath-CoT 字段结构；
- 建立 evaluator unit tests；
- 输出 `results/public_dataset_inspect.md` 和 `results/evaluator_test.json`。

## Stage Plan
- Stage 0：环境与仓库初始化
- Stage 1：Smoke Test，仅验证流程
- Stage 2：Scoring Protocol and Dataset Inspection，评分协议与公开数据集字段检查
- Stage 3：Build Formal Number Theory Evaluation Set，构造正式数论评测集
- Stage 4：Formal Baseline Evaluation，正式 baseline 评测
- Stage 5：Prepare NuminaMath-1.5 Number Theory SFT Data，准备数论 SFT 训练数据
- Stage 6：LoRA SFT，数论领域 LoRA 微调
- Stage 7：Teacher Response Distillation，教师答案蒸馏
- Stage 8：GRPO，基于规则奖励的强化学习微调
- Stage 9：Optional Logit Distillation，可选白盒 logits 蒸馏
- Stage 10：Demo and Final Packaging，Demo 和最终项目包装

## Key Decisions
- 第一版正式目标只做数论方向，不再同时覆盖代数。
- 正式评测集使用公开数论竞赛题，目标规模 200 道。
- 正式训练数据来自 NuminaMath-1.5 Number Theory 子集。
- 主指标是 Final Answer Accuracy。
- Math-Verify 为主评分器，自定义规则为 fallback。
- 证明题、图片题、开放题暂时不进入主评测。

## Execution Rule
All training, evaluation, model downloading, Hugging Face cache, data preprocessing, checkpoint saving, and git operations must be executed on the remote 2x RTX4090 server. Local Windows is only used for VSCode Remote-SSH editing and connection. Do not run model inference or training locally.

## Next Stage
Stage 3 - Build Formal Number Theory Evaluation Set

## Git Rule
每个阶段结束后更新 CONTEXT.md，执行 git commit 并 push。不要提交 data/raw、data/processed、outputs、checkpoints、models、Hugging Face cache、模型权重、wandb 日志或大文件。

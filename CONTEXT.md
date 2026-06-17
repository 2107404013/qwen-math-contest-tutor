# CONTEXT.md

## Project Name
NumberTheory-Qwen

## Project Goal
NumberTheory-Qwen：面向高中竞赛数论题的轻量级数学问答助手。

## Student Model
Qwen/Qwen2.5-Math-1.5B-Instruct

## Teacher Model
Qwen/Qwen2.5-Math-7B-Instruct

## Target Domain
High-school olympiad number theory

## Current Stage
Project Refactor before Stage 2

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

Stage 1 的 30 题结果只用于验证数据读取、模型加载、生成、评分和结果保存流程，不作为正式 baseline。正式 baseline 后续使用 `data/processed/public_number_theory_eval.jsonl`。

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

## Next Stage
Stage 2 - Scoring Protocol and Dataset Inspection

## Execution Rule
All training, evaluation, model downloading, Hugging Face cache, data preprocessing, checkpoint saving, and git operations must be executed on the remote 2×RTX4090 server. Local Windows is only used for VSCode Remote-SSH editing and connection. Do not run model inference or training locally.

## Git Rule
不要提交 data/raw、data/processed、outputs、checkpoints、models、Hugging Face cache、模型权重、wandb 日志或大文件。

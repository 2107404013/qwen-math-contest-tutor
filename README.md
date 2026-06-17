# NumberTheory-Qwen

NumberTheory-Qwen：面向高中竞赛数论题的轻量级数学问答助手。

## 项目目标

基于 `Qwen/Qwen2.5-Math-1.5B-Instruct`，构建专注高中竞赛数论方向的数学问答助手。训练路线为 Formal Baseline → LoRA SFT → Teacher Response Distillation → GRPO → Optional Logit Distillation。

## 模型选择

- 学生模型：`Qwen/Qwen2.5-Math-1.5B-Instruct`
- 教师模型：`Qwen/Qwen2.5-Math-7B-Instruct`
- Prompt 语言：中文

## 为什么第一版只做数论

- 数论领域边界更清楚；
- 数据筛选更容易；
- 题目通常有明确最终答案；
- 更适合 rule-based evaluation 和 GRPO reward；
- 更容易在小规模训练中观察到提升。

## 为什么暂时不同时做代数

- 代数覆盖范围太广；
- 答案形式更复杂；
- baseline 可能较高；
- 第一版项目需要先保证评测可信和结果可解释。

## 阶段流程

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

## 数据与评测

- `eval_small.jsonl` 只是 Stage 1 smoke test，用于验证数据读取、模型加载、生成、评分和结果保存流程，不作为正式 baseline。
- 正式评测集是 `data/processed/public_number_theory_eval.jsonl`。
- 正式评测规模为 200 道公开高中竞赛数论题。
- 正式训练数据来自 `NuminaMath-1.5` 的 Number Theory 子集，第一版 5k 条，确认提升后扩展到 10k 条。
- 证明题、图片题、开放题暂时不进入主评测。

## Scoring Protocol

主指标是 Final Answer Accuracy。

评分标准以 Math-Verify final-answer equivalence 为主，自定义 normalize、列表答案判断、分数/小数处理、等式右侧提取和 SymPy 等价判断作为 fallback。

辅助指标包括 Boxed Answer Rate、Extraction Success Rate、Error Type Distribution。

## 大文件规则

不要上传 `data/raw/`、`data/processed/`、`outputs/`、`checkpoints/`、`models/`、Hugging Face cache、模型权重、wandb 日志或大文件。

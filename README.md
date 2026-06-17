# NumberTheory-Qwen

NumberTheory-Qwen：面向高中竞赛数论题的轻量级数学问答助手。

## 项目目标

基于 `Qwen/Qwen2.5-Math-1.5B-Instruct`，构建专注高中竞赛数论方向的数学问答助手。项目路线为 Formal Baseline -> LoRA SFT -> Teacher Response Distillation -> GRPO -> Optional Logit Distillation。

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

本阶段不训练模型、不运行模型推理、不下载 Qwen 模型权重，只完成评分协议和公开数据集字段检查。

正式评分协议：

- 主指标：Final Answer Accuracy；
- 主评分器：Math-Verify final-answer equivalence；
- fallback：字符串归一化、列表答案判断、分数/小数等价、等式右侧提取、简单 SymPy 等价；
- 辅助指标：Boxed Answer Rate、Extraction Success Rate、Error Type Distribution；
- 证明题、图片题、开放题和长解答题暂时标记为 `unsuitable_for_rule_eval`，不进入主评测。

公开数据集检查对象：

- Omni-MATH-Rule / Omni-MATH：候选正式数论评测来源；
- NuminaMath-1.5：候选数论 SFT 训练来源；
- NuminaMath-CoT：备用训练来源。

## 文件结构

```text
configs/      配置文件
scripts/      数据处理、评测、训练和 demo 脚本
data/         数据说明；raw 和 processed 不上传 Git
results/      小规模结果和分析文件
outputs/      本地训练输出，不上传 Git
checkpoints/  本地 checkpoint，不上传 Git
models/       本地模型权重，不上传 Git
```

## 大文件规则

不要上传 `data/raw/`、`data/processed/`、`outputs/`、`checkpoints/`、`models/`、Hugging Face cache、模型权重、wandb 日志或大文件。

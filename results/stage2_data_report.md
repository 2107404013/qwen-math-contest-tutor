# Stage 2 数据准备报告

本阶段构建了一个小规模高中竞赛代数与数论 SFT 种子数据集，用于后续 LoRA SFT 流程验证。

## 数据规模

- 总样本数：12
- 训练集：10
- 验证集：2
- 代数样本：6
- 数论样本：6

## 数据格式

每条样本保存为 jsonl，包含 id、subject、problem、answer、solution 和 messages 字段。

messages 字段采用 chat instruction 格式，后续可直接用于 LoRA SFT。

## 输出文件

- data/processed/sft_train.jsonl
- data/processed/sft_val.jsonl

注意：data/processed/ 已被 .gitignore 忽略，不应提交到 GitHub。

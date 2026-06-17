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

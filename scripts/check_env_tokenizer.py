from __future__ import annotations

from dataclasses import dataclass

from transformers import AutoConfig, AutoTokenizer


STUDENT_NAME = "Qwen/Qwen2.5-Math-1.5B-Instruct"
TEACHER_NAME = "Qwen/Qwen2.5-Math-7B-Instruct"
TEST_TEXT = "已知 x^2-5x+6=0，求 x 的值。"


@dataclass(frozen=True)
class TorchInfo:
    available: bool
    cuda_available: bool = False
    gpu_count: int = 0
    gpu_lines: tuple[str, ...] = ()
    error: str | None = None


def inspect_torch() -> TorchInfo:
    try:
        import torch
    except Exception as exc:  # pragma: no cover - environment dependent
        return TorchInfo(available=False, error=repr(exc))

    cuda_available = torch.cuda.is_available()
    gpu_count = torch.cuda.device_count() if cuda_available else 0
    gpu_lines: list[str] = []

    for idx in range(gpu_count):
        props = torch.cuda.get_device_properties(idx)
        memory_gb = props.total_memory / 1024**3
        gpu_lines.append(f"GPU {idx}: {props.name}, {memory_gb:.2f} GB")

    return TorchInfo(
        available=True,
        cuda_available=cuda_available,
        gpu_count=gpu_count,
        gpu_lines=tuple(gpu_lines),
    )


def print_torch_info() -> None:
    info = inspect_torch()
    print("== Torch / GPU ==")
    print(f"torch import available: {info.available}")

    if info.error:
        print(f"torch import error: {info.error}")
        print()
        return

    print(f"cuda available: {info.cuda_available}")
    print(f"gpu count: {info.gpu_count}")
    if info.gpu_lines:
        for line in info.gpu_lines:
            print(line)
    else:
        print("GPU: none detected")
    print()


def main() -> None:
    print_torch_info()

    print("== Tokenizer / Config ==")
    print(f"student model: {STUDENT_NAME}")
    print(f"teacher model: {TEACHER_NAME}")
    print("loading tokenizer/config only; model weights are not loaded")

    tok_s = AutoTokenizer.from_pretrained(STUDENT_NAME, trust_remote_code=True)
    tok_t = AutoTokenizer.from_pretrained(TEACHER_NAME, trust_remote_code=True)
    cfg_s = AutoConfig.from_pretrained(STUDENT_NAME, trust_remote_code=True)
    cfg_t = AutoConfig.from_pretrained(TEACHER_NAME, trust_remote_code=True)

    student_len = len(tok_s)
    teacher_len = len(tok_t)
    student_vocab_size = cfg_s.vocab_size
    teacher_vocab_size = cfg_t.vocab_size
    vocab_equal = tok_s.get_vocab() == tok_t.get_vocab()
    encode_equal = tok_s.encode(TEST_TEXT) == tok_t.encode(TEST_TEXT)
    common_vocab = min(student_len, teacher_len, student_vocab_size, teacher_vocab_size)

    print(f"student len(tokenizer): {student_len}")
    print(f"teacher len(tokenizer): {teacher_len}")
    print(f"student config vocab_size: {student_vocab_size}")
    print(f"teacher config vocab_size: {teacher_vocab_size}")
    print(f"test text: {TEST_TEXT}")
    print(f"test encode equal: {encode_equal}")
    print(f"get_vocab equal: {vocab_equal}")
    print(f"common_vocab for logits KD: {common_vocab}")
    print()

    print("== Distillation Conclusion ==")
    if vocab_equal and encode_equal:
        print("White-box logits distillation is compatible over the shared tokenizer vocabulary.")
    else:
        print("White-box logits distillation is not directly compatible; tokenizer alignment must be fixed first.")

    if student_vocab_size != teacher_vocab_size:
        print(
            "config vocab_size differs; compute KL only on logits[..., :common_vocab] "
            "during future white-box distillation."
        )
    else:
        print("config vocab_size matches; full-vocab KL is shape-compatible.")


if __name__ == "__main__":
    main()

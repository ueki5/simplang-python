from __future__ import annotations

from simplang.compiler import Instr, Push, IAdd, ISub, IMul, IDiv, INeg


def generate_asm(instrs: list[Instr]) -> str:
    lines: list[str] = []

    lines += [
        "    .text",
        "    .globl main",
        "main:",
        "    pushq %rbp",
        "    movq  %rsp, %rbp",
    ]

    for instr in instrs:
        match instr:
            case Push(value=v):
                lines.append(f"    pushq ${v}")
            case IAdd():
                lines += [
                    "    popq  %rax",
                    "    popq  %rbx",
                    "    addq  %rbx, %rax",
                    "    pushq %rax",
                ]
            case ISub():
                # rax = right (top), rbx = left; result = rbx - rax
                lines += [
                    "    popq  %rax",
                    "    popq  %rbx",
                    "    subq  %rax, %rbx",
                    "    pushq %rbx",
                ]
            case IMul():
                lines += [
                    "    popq  %rax",
                    "    popq  %rbx",
                    "    imulq %rbx, %rax",
                    "    pushq %rax",
                ]
            case IDiv():
                lines += [
                    "    popq  %rcx",
                    "    testq %rcx, %rcx",
                    "    je    .Ldiv_zero_error",
                    "    popq  %rax",
                    "    cqto",
                    "    idivq %rcx",
                    "    pushq %rax",
                ]
            case INeg():
                lines += [
                    "    popq  %rax",
                    "    negq  %rax",
                    "    pushq %rax",
                ]

    lines += [
        "    popq  %rsi",
        "    leaq  .Lfmt(%rip), %rdi",
        "    xorl  %eax, %eax",
        "    call  printf@PLT",
        "    xorl  %eax, %eax",
        "    popq  %rbp",
        "    ret",
        ".Ldiv_zero_error:",
        "    leaq  .Lerr(%rip), %rdi",
        "    call  puts@PLT",
        "    movl  $1, %edi",
        "    call  exit@PLT",
        "    .section .rodata",
        ".Lfmt:",
        '    .string "%d\\n"',
        ".Lerr:",
        '    .string "error: division by zero"',
        '    .section .note.GNU-stack,"",@progbits',
    ]

    return "\n".join(lines) + "\n"

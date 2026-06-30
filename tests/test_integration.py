import subprocess
import tempfile
from pathlib import Path

from minclang.compiler import tokenize, parse, compile_expr
from minclang.codegen import generate_asm


def compile_and_run(source: str) -> str:
    tokens = tokenize(source)
    ast = parse(tokens)
    instrs = compile_expr(ast)
    asm = generate_asm(instrs)

    with tempfile.TemporaryDirectory() as tmpdir:
        asm_file = Path(tmpdir) / "out.s"
        bin_file = Path(tmpdir) / "out"
        asm_file.write_text(asm)
        subprocess.run(
            ["gcc", str(asm_file), "-o", str(bin_file)],
            check=True,
            capture_output=True,
        )
        result = subprocess.run(
            [str(bin_file)],
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()


def test_lit():
    assert compile_and_run("42") == "42"


def test_add():
    assert compile_and_run("3 + 4") == "7"


def test_sub():
    assert compile_and_run("5 - 3") == "2"


def test_mul():
    assert compile_and_run("2 * 6") == "12"


def test_div():
    assert compile_and_run("6 / 3") == "2"


def test_neg():
    assert compile_and_run("-5") == "-5"


def test_complex():
    # 1 + 2 * (3 - 4) = 1 + 2 * (-1) = 1 - 2 = -1
    assert compile_and_run("1 + 2 * (3 - 4)") == "-1"


def test_div_zero_exits_nonzero():
    tokens = tokenize("10 / 0")
    ast = parse(tokens)
    instrs = compile_expr(ast)
    asm = generate_asm(instrs)

    with tempfile.TemporaryDirectory() as tmpdir:
        asm_file = Path(tmpdir) / "out.s"
        bin_file = Path(tmpdir) / "out"
        asm_file.write_text(asm)
        subprocess.run(["gcc", str(asm_file), "-o", str(bin_file)], check=True, capture_output=True)
        result = subprocess.run([str(bin_file)], capture_output=True)
        assert result.returncode != 0

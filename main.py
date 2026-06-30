import argparse
import subprocess
import tempfile
from pathlib import Path

from simplang.compiler import tokenize, parse, compile_expr
from simplang.codegen import generate_asm


def main() -> None:
    ap = argparse.ArgumentParser(
        prog="simplang",
        description="Compile an arithmetic expression to a native binary",
    )
    ap.add_argument("file", help="source file to compile")
    ap.add_argument("-o", metavar="NAME", default="out", help="output binary name (default: out)")
    ap.add_argument("-S", metavar="ASM_FILE", help="save assembly source to FILE")
    args = ap.parse_args()

    source = Path(args.file).read_text()
    tokens = tokenize(source)
    ast = parse(tokens)
    instrs = compile_expr(ast)
    asm = generate_asm(instrs)

    if args.S:
        Path(args.S).write_text(asm)

    with tempfile.NamedTemporaryFile(suffix=".s", mode="w", delete=False) as f:
        asm_path = f.name
        f.write(asm)

    try:
        subprocess.run(["gcc", asm_path, "-o", args.o], check=True)
    finally:
        Path(asm_path).unlink(missing_ok=True)


if __name__ == "__main__":
    main()

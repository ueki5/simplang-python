# simplang-python

算術式を受け取ってネイティブバイナリにコンパイルする、教育目的のミニマルコンパイラです。

## プロジェクト概要

ソースファイルに書かれた算術式（整数リテラルと四則演算）をトークナイズ・パース・スタックIRへのコンパイル・x86-64アセンブリ生成という4段階のパイプラインで処理し、gccでネイティブバイナリを生成します。

## アーキテクチャ

```
ソースファイル
    ↓ tokenize()
Token列 (TokInt | TokPlus | TokMinus | TokStar | TokSlash | TokLParen | TokRParen)
    ↓ parse()
AST (Lit | Add | Sub | Mul | Div | Neg)
    ↓ compile_expr()
スタックIR (Push | IAdd | ISub | IMul | IDiv | INeg)
    ↓ generate_asm()
x86-64 AT&T記法アセンブリ
    ↓ gcc
ネイティブバイナリ
```

### 各モジュール

| ファイル | 役割 |
|---|---|
| `simplang/compiler.py` | トークナイザ・パーサ・スタックIRコンパイラ。Token型・Expr型・Instr型の定義も含む |
| `simplang/codegen.py` | スタックIRリストからx86-64 AT&T記法アセンブリ文字列を生成 |
| `main.py` | CLIエントリポイント。`-o`で出力バイナリ名、`-S`でアセンブリファイル保存 |

## 言語仕様

- 整数リテラル（非負整数）
- 四則演算：`+` `-` `*` `/`
- 単項マイナス：`-expr`
- 括弧による優先順位制御
- 演算子優先順位：`*` `/` > `+` `-`（標準的な算術優先順位）
- ゼロ除算：バイナリ実行時に `error: division by zero` を出力してexit code 1で終了

## 開発環境

- Python 3.12（`uv` で管理）
- 依存ライブラリなし（devのみ `pytest>=8.0`）
- テスト実行はアセンブル・リンクにgccが必要

## よく使うコマンド

```bash
# テスト実行
uv run pytest

# コンパイル（算術式をファイルに書いて渡す）
echo "1 + 2 * (3 - 4)" > expr.txt
uv run python main.py expr.txt -o out

# アセンブリを確認しながらコンパイル
uv run python main.py expr.txt -o out -S out.s
```

## コード生成の詳細

生成されるアセンブリはスタックマシン方式です。

- `Push(v)` → `pushq $v`
- `IAdd` → popでrax・rbxに取り出し、`addq`して結果をpush
- `ISub` → `rbx - rax`（左辺 - 右辺）の順で計算
- `IMul` → `imulq`で符号付き整数乗算
- `IDiv` → `cqto` + `idivq`で符号付き整数除算。ゼロ除算は`.Ldiv_zero_error`ラベルへジャンプ
- `INeg` → `negq`で符号反転
- 最終結果は`printf("%d\n", result)`で標準出力へ

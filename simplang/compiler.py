from __future__ import annotations
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Token types
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class TokInt:
    value: int

@dataclass(frozen=True)
class TokPlus:
    pass

@dataclass(frozen=True)
class TokMinus:
    pass

@dataclass(frozen=True)
class TokStar:
    pass

@dataclass(frozen=True)
class TokSlash:
    pass

@dataclass(frozen=True)
class TokLParen:
    pass

@dataclass(frozen=True)
class TokRParen:
    pass

type Token = TokInt | TokPlus | TokMinus | TokStar | TokSlash | TokLParen | TokRParen


# ---------------------------------------------------------------------------
# AST (Expr) types
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Lit:
    value: int

@dataclass(frozen=True)
class Add:
    left: Expr
    right: Expr

@dataclass(frozen=True)
class Sub:
    left: Expr
    right: Expr

@dataclass(frozen=True)
class Mul:
    left: Expr
    right: Expr

@dataclass(frozen=True)
class Div:
    left: Expr
    right: Expr

@dataclass(frozen=True)
class Neg:
    operand: Expr

type Expr = Lit | Add | Sub | Mul | Div | Neg


# ---------------------------------------------------------------------------
# Stack IR (Instr) types — I-prefix avoids shadowing Expr names
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Push:
    value: int

@dataclass(frozen=True)
class IAdd:
    pass

@dataclass(frozen=True)
class ISub:
    pass

@dataclass(frozen=True)
class IMul:
    pass

@dataclass(frozen=True)
class IDiv:
    pass

@dataclass(frozen=True)
class INeg:
    pass

type Instr = Push | IAdd | ISub | IMul | IDiv | INeg


# ---------------------------------------------------------------------------
# Tokenizer
# ---------------------------------------------------------------------------

class TokenizeError(Exception):
    pass


def tokenize(source: str) -> list[Token]:
    tokens: list[Token] = []
    i = 0
    while i < len(source):
        c = source[i]
        if c.isspace():
            i += 1
        elif c.isdigit():
            j = i
            while j < len(source) and source[j].isdigit():
                j += 1
            tokens.append(TokInt(int(source[i:j])))
            i = j
        elif c == '+':
            tokens.append(TokPlus())
            i += 1
        elif c == '-':
            tokens.append(TokMinus())
            i += 1
        elif c == '*':
            tokens.append(TokStar())
            i += 1
        elif c == '/':
            tokens.append(TokSlash())
            i += 1
        elif c == '(':
            tokens.append(TokLParen())
            i += 1
        elif c == ')':
            tokens.append(TokRParen())
            i += 1
        else:
            raise TokenizeError(f"unexpected character: {c!r}")
    return tokens


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

class ParseError(Exception):
    pass


class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self._tokens = tokens
        self._pos = 0

    def parse(self) -> Expr:
        expr = self._expr()
        if self._pos != len(self._tokens):
            raise ParseError(f"unexpected token at position {self._pos}")
        return expr

    def _peek(self) -> Token | None:
        if self._pos < len(self._tokens):
            return self._tokens[self._pos]
        return None

    def _advance(self) -> Token:
        tok = self._tokens[self._pos]
        self._pos += 1
        return tok

    def _expr(self) -> Expr:
        # expr ::= term (('+' | '-') term)*
        node = self._term()
        while True:
            match self._peek():
                case TokPlus():
                    self._advance()
                    node = Add(node, self._term())
                case TokMinus():
                    self._advance()
                    node = Sub(node, self._term())
                case _:
                    break
        return node

    def _term(self) -> Expr:
        # term ::= factor (('*' | '/') factor)*
        node = self._factor()
        while True:
            match self._peek():
                case TokStar():
                    self._advance()
                    node = Mul(node, self._factor())
                case TokSlash():
                    self._advance()
                    node = Div(node, self._factor())
                case _:
                    break
        return node

    def _factor(self) -> Expr:
        # factor ::= INT | '(' expr ')' | '-' factor
        match self._peek():
            case TokInt(value=v):
                self._advance()
                return Lit(v)
            case TokLParen():
                self._advance()
                node = self._expr()
                if not isinstance(self._peek(), TokRParen):
                    raise ParseError("expected ')'")
                self._advance()
                return node
            case TokMinus():
                self._advance()
                return Neg(self._factor())
            case tok:
                raise ParseError(f"unexpected token: {tok!r}")


def parse(tokens: list[Token]) -> Expr:
    return Parser(tokens).parse()


# ---------------------------------------------------------------------------
# IR Compiler
# ---------------------------------------------------------------------------

def compile_expr(expr: Expr) -> list[Instr]:
    out: list[Instr] = []
    _compile(expr, out)
    return out


def _compile(expr: Expr, out: list[Instr]) -> None:
    match expr:
        case Lit(value=v):
            out.append(Push(v))
        case Add(left=l, right=r):
            _compile(l, out)
            _compile(r, out)
            out.append(IAdd())
        case Sub(left=l, right=r):
            _compile(l, out)
            _compile(r, out)
            out.append(ISub())
        case Mul(left=l, right=r):
            _compile(l, out)
            _compile(r, out)
            out.append(IMul())
        case Div(left=l, right=r):
            _compile(l, out)
            _compile(r, out)
            out.append(IDiv())
        case Neg(operand=o):
            _compile(o, out)
            out.append(INeg())

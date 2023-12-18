"""
"""

import enum
import lark

from . import types as tt


class TreeData(enum.StrEnum):
    start = enum.auto()
    user_field = enum.auto()
    prop = enum.auto()
    constraints = enum.auto()
    constraint = enum.auto()
    args = enum.auto()
    arg = enum.auto()
    ret = enum.auto()
    fields = enum.auto()


class TokenType(enum.StrEnum):
    RULE = enum.auto()
    LCASE_LETTER = "LCASE_LETTER"
    INT = "INT"


type Child = lark.Token | lark.ParseTree


def _parse_rank(child: Child) -> tt.Rank:
    assert isinstance(child, lark.Token)
    match child.type:
        case TokenType.INT:
            return int(child.value)
        case TokenType.LCASE_LETTER:
            return tt.Var(child.value)
        case _:
            raise ValueError("SyntaxError")


def _parse_field(child: Child) -> tt.Var | tt.ConcreteField:
    assert isinstance(child, lark.Token)
    match child.type:
        case TokenType.LCASE_LETTER:
            return tt.Var(child.value)
        case _:
            return str(child.value)


def _parse_var(child: Child) -> tt.Var:
    assert isinstance(child, lark.Token)
    assert child.type == TokenType.LCASE_LETTER
    return tt.Var(child.value)


def parse_ret(child: Child) -> tt.GeneralType:
    assert not isinstance(child, lark.Token)
    assert child.data == TreeData.ret
    field = _parse_field(child.children[-1])
    ranks = tuple(_parse_rank(x) for x in child.children[:-1])
    return tt.GeneralType(field=field, ranks=ranks)


def parse_arg(child: Child) -> tt.Arg:
    assert not isinstance(child, lark.Token)
    assert child.data == TreeData.arg
    assert len(child.children) == 2
    var = _parse_var(child.children[0])
    ret = parse_ret(child.children[1])
    return tt.Arg(var=var, ret=ret)


def parse_start(tree: lark.ParseTree):
    x1 = [
        parse_ret(x) for x in tree.find_pred(lambda x: x.data == TreeData.ret)
    ]
    x2 = [
        parse_arg(x) for x in tree.find_pred(lambda x: x.data == TreeData.arg)
    ]
    print(x1)
    print(x2)
    return (x1, x2)

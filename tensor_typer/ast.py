"""
"""

import typing as t
import enum
import lark

from . import types as tt


class TokenValue(enum.StrEnum):
    start = enum.auto()
    decl = enum.auto()
    alias = enum.auto()
    alias_name = enum.auto()
    type_constraint = enum.auto()
    arg = enum.auto()
    general_type = enum.auto()
    concrete_type = enum.auto()
    rank = enum.auto()
    atomic_type = enum.auto()
    var = enum.auto()


class TokenType(enum.StrEnum):
    RULE = enum.auto()


Child: t.TypeAlias = lark.Token | lark.ParseTree


def parse_general_type(child: Child) -> tt.GeneralType:
    ...


def parse_arg(child: Child) -> tt.Arg:
    ...


def parse_type_constraint(child: Child) -> tt.TypeConstraint:
    ...


def parse_alias(child: Child) -> tt.Alias:
    ...


def parse_decl(child: Child) -> tt.Decl:
    ...


def parse_start(child: Child) -> tt.Namespace:
    ...


# def parse_field(child: Child) -> Field:
#     assert not isinstance(child, lark.Token)
#     match child.data:
#         case TokenValue.abstract_field:
#             assert len(child.children) == 1
#             binding = child.children[0]
#             assert isinstance(binding, lark.Token)
#             return tt.AbstractField(tt.LcaseLetter(binding))
#         case TokenValue.atomic_type:
#             assert len(child.children) == 1
#             binding = child.children[0]
#             assert not isinstance(binding, lark.Token)
#             return tt.ConcreteField(base=tt.Field(binding.data))
#         case _:
#             print(child)
#             raise ValueError()


# def parse_rank(child: Child) -> tt.Rank:
#     assert not isinstance(child, lark.Token)
#     assert child.data == TokenValue.rank
#     assert len(child.children) == 1
#     rank_type = child.children[0]
#     assert not isinstance(rank_type, lark.Token)
#     assert len(rank_type.children) == 1

#     match rank_type.data:
#         case TokenValue.abstract_size:
#             assert len(rank_type.children) == 1
#             binding = rank_type.children[0]
#             assert isinstance(binding, lark.Token)
#             rank = tt.AbstractSize(binding=tt.LcaseLetter(binding))
#         case TokenValue.concrete_size:
#             assert len(rank_type.children) == 1
#             size = rank_type.children[0]
#             assert isinstance(size, lark.Token)
#             rank = tt.ConcreteSize(size=int(size))
#         case _:
#             breakpoint()
#             raise ValueError()
#     return tt.Rank(rank=rank)


# def parse_term(child: Child) -> tt.Tensor:
#     assert not isinstance(child, lark.Token)
#     assert child.data == TokenValue.general_type
#     type_ = parse_field(child.children[-1])
#     ranks = tuple(parse_rank(child) for child in child.children[:-1])
#     return tt.Tensor(field=type_, ranks=ranks)


# def parse_arg(child: Child) -> tt.Arg:
#     assert not isinstance(child, lark.Token)
#     assert child.data == TokenValue.arg
#     assert len(child.children) == 2
#     binding, term = child.children
#     assert isinstance(binding, lark.Token)
#     assert not isinstance(term, lark.Token)
#     return tt.Arg(binding=tt.LcaseLetter(binding), term=parse_term(term))


# def parse_decl(child: Child) -> tt.Decl:
#     assert not isinstance(child, lark.Token)
#     assert child.data == TokenValue.decl
#     assert len(child.children) >= 2
#     name = child.children[0]
#     assert isinstance(name, lark.Token)
#     if len(name.value) == 1:
#         raise ValueError("decl name can't be a single character long")
#     assert isinstance(name, lark.Token)
#     ret = parse_term(child.children[-1])
#     args = tuple(parse_arg(child) for child in child.children[1:-1])
#     return tt.Decl(name=str(name), ret=ret, args=args)


# def parse_start(tree: lark.ParseTree) -> Namespace:
#     assert tree.data == TokenValue.start
#     decls = [parse_decl(decl) for decl in tree.children]
#     return {decl.name: decl for decl in decls}

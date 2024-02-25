"""
"""

import enum
import typing as t
from collections import abc

import lark

from simiya import datatypes as tt


class TreeData(enum.StrEnum):
    start = enum.auto()
    user_field = enum.auto()
    fn = enum.auto()
    fn_body = enum.auto()
    expr = enum.auto()
    inodes = enum.auto()
    inode = enum.auto()
    constraints = enum.auto()
    constraint = enum.auto()
    args = enum.auto()
    arg = enum.auto()
    ret = enum.auto()
    fields = enum.auto()
    static_rank = enum.auto()
    bound_rank = enum.auto()


class TokenType(enum.StrEnum):
    RULE = enum.auto()
    LCASE_LETTER = "LCASE_LETTER"
    INT = "INT"
    VARNAME = "VARNAME"
    RANK = "RANK"
    CONCRETE_FIELD = "CONCRETE_FIELD"
    ATOMIC_FIELD = "ATOMIC_FIELD"
    SYMBOL = "SYMBOL"
    TYPE_SYMBOL = "TYPE_SYMBOL"


Child: t.TypeAlias = lark.Token | lark.ParseTree


def _parse_rank(child: Child) -> tt.Rank:
    assert not isinstance(child, lark.Token)
    assert len(child.children) == 1
    val_ = child.children[0]
    assert isinstance(val_, lark.Token)
    match child.data:
        case TreeData.static_rank:
            return int(val_)
        case TreeData.bound_rank:
            return tt.VarName(val_)
        case _:
            raise ValueError("SyntaxError")


def _parse_field(child: Child) -> tt.VarName | tt.ConcreteField:
    assert isinstance(child, lark.Token)
    match child.type:
        case TokenType.VARNAME:
            return tt.VarName(child.value)
        case TokenType.CONCRETE_FIELD:
            return str(child.value)
        case _:
            raise ValueError("wrong field type: %s", child.type)


def parse_VARNAME(child: Child) -> tt.VarName:
    assert isinstance(child, lark.Token)
    assert child.type == TokenType.VARNAME
    return tt.VarName(child.value)


def parse_tensor_annotation(child: Child) -> tt.TensorType:
    assert not isinstance(child, lark.Token)
    assert child.data == TreeData.ret
    field = _parse_field(child.children[-1])
    ranks = tuple(_parse_rank(x) for x in child.children[:-1])
    return tt.TensorType(field=field, ranks=ranks)


def parse_argument(child: Child) -> tt.NamedType:
    assert not isinstance(child, lark.Token)
    assert child.data == TreeData.arg
    assert len(child.children) == 2
    var = parse_VARNAME(child.children[0])
    ret = parse_tensor_annotation(child.children[1])
    return tt.NamedType(name=var, type_=ret)


def _parse_fieldclass(child: Child) -> tt.FieldClass:
    assert not isinstance(child, lark.Token)
    assert child.data == TreeData.fields
    return frozenset(str(x) for x in child.children)


def parse_user_field(child: Child) -> tt.GlobalSumType:
    assert not isinstance(child, lark.Token)
    assert child.data == TreeData.user_field
    assert len(child.children) == 2
    (_var, _fieldclass) = child.children
    assert isinstance(_var, lark.Token)
    binding = str(_var)
    fieldclass = _parse_fieldclass(_fieldclass)
    return tt.SumType(symbol=binding, group=fieldclass)


def parse_local_constraint(child: Child) -> tt.LocalSumType:
    assert not isinstance(child, lark.Token)
    assert child.data == TreeData.constraint
    assert len(child.children) == 2
    (binding_, fieldclass_) = child.children
    assert isinstance(binding_, lark.Token)
    binding = parse_VARNAME(binding_)
    fieldclass = _parse_fieldclass(fieldclass_)
    return tt.SumType(binding, fieldclass)


def parse_local_constraints(child: Child) -> frozenset[tt.LocalSumType]:
    assert not isinstance(child, lark.Token)
    assert child.data == TreeData.constraints
    return frozenset(parse_local_constraint(x) for x in child.children)


def parse_arguments(child: Child) -> tuple[tt.NamedType, ...]:
    assert not isinstance(child, lark.Token)
    assert child.data == TreeData.args
    return tuple(parse_argument(x) for x in child.children)


def parse_expression(child: Child) -> tt.Expression:
    assert not isinstance(child, lark.Token)
    assert child.data == TreeData.expr
    fn_name_ = child.children[0]
    nodes_ = child.children[1:]
    fn_name = str(fn_name_)
    nodes = tuple(parse_VARNAME(i) for i in nodes_)
    return tt.Expression(fn_name, nodes)


def parse_inode(child: Child) -> tt.NamedExpression:
    assert not isinstance(child, lark.Token)
    assert child.data == TreeData.inode
    assert len(child.children) == 2
    (varname_, expr_) = child.children
    varname = parse_VARNAME(varname_)
    expr = parse_expression(expr_)
    return tt.NamedExpression(varname, expr)


def parse_inodes(child: Child) -> tuple[tt.NamedExpression, ...]:
    assert not isinstance(child, lark.Token)
    assert child.data == TreeData.inodes
    return tuple(parse_inode(i) for i in child.children)


def parse_fn_body(child: Child) -> tt.FnBody | None:
    assert not isinstance(child, lark.Token)
    assert child.data == TreeData.fn_body
    match len(child.children):
        case 0:
            return None
        case 1:
            raise AssertionError(
                "Expected inodes and terminal, only received 1"
            )
        case 2:
            (inodes_, terminal_) = child.children
            inodes = parse_inodes(inodes_)
            terminal = parse_expression(terminal_)
            return tt.FnBody(inodes, terminal)
        case _:
            raise AssertionError("I'm not sure what I got.")


def get_new_varname(fn_namespace: abc.Container[tt.VarName]) -> tt.VarName:
    for candidate_varname in tt.VarName:
        if candidate_varname in fn_namespace:
            continue
        else:
            return candidate_varname
    raise ValueError("Ran out of local variable names!")


def parse_fn(child: Child) -> tt.FnDefAst | tt.FnDeclAst:
    assert not isinstance(child, lark.Token)
    assert child.data == TreeData.fn
    (constraints_, binding_, args_, ret_, fn_body_) = child.children
    binding = str(binding_)
    constraints = parse_local_constraints(constraints_)
    args = parse_arguments(args_)
    ret = parse_tensor_annotation(ret_)
    body = parse_fn_body(fn_body_)
    if body is None:
        return tt.FnDeclAst(
            symbol=binding,
            constraints=constraints,
            acns={x.name: x for x in args},
            ret=ret,
        )
    else:
        # return tt.Fn(binding, constraints, args, ret, body)
        fn_namespace: tt.LocalNamespace = {}

        for compute_node in (*args, *body.inodes):
            if compute_node.name in fn_namespace:
                raise ValueError("Same variable defined multiple times")

        for compute_node in args:
            fn_namespace[compute_node.name] = tt.NodeT.ACN

        for compute_node in body.inodes:
            fn_namespace[compute_node.name] = tt.NodeT.ICN

        # for inode in body.inodes:
        #     if inode.value.fn_symbol not in namespace:
        #         raise ValueError(
        #             f"unknown symbol ({inode.value.fn_symbol} not in namespace)"
        #         )

        terminal_varname = get_new_varname(fn_namespace)

        fn_namespace[terminal_varname] = tt.NodeT.TCN

        terminal_node = tt.TypedNamedExpression(
            name=terminal_varname, value=body.terminal, type_=ret
        )

        return tt.FnDefAst(
            symbol=binding,
            constraints=constraints,
            namespace=fn_namespace,
            icns={x.name: x.value for x in body.inodes},
            tcn=terminal_node,
            acns={x.name: x for x in args},
        )


def match_toplvl_def(
    child: Child,
) -> tt.FnDefAst | tt.FnDeclAst | tt.GlobalSumType:
    assert not isinstance(child, lark.Token)
    match child.data:
        case TreeData.user_field:
            return parse_user_field(child)
        case TreeData.fn:
            return parse_fn(child)
        case _:
            raise ValueError("unknown top-level tree object.")


def ast_convert(tree: lark.ParseTree) -> tt.Module:
    values = [
        match_toplvl_def(x)
        for x in t.cast(list[lark.Tree[lark.Token]], tree.children)
    ]

    fn_defs: tt.FnDefNamespace = {}
    fn_decls: tt.FnDeclNamespace = {}
    sum_types: tt.SumTypeNamespace = {}
    symbols: tt.SymbolNamespace = {}

    for toplvl in values:
        symbol = toplvl.symbol
        if symbol in symbols:
            raise ValueError(f"Duplicate symbol: {symbol}.")
        match toplvl:
            case tt.SumType():
                sum_types[symbol] = toplvl
                symbols[symbol] = tt.ModScopeT.SUM_TYPE
            case tt.FnDeclAst():
                fn_decls[symbol] = toplvl
                symbols[symbol] = tt.ModScopeT.FN_DECL
            case tt.FnDefAst():
                fn_defs[symbol] = toplvl
                symbols[symbol] = tt.ModScopeT.FN_DEF

    return tt.Module(symbols, sum_types, fn_decls, fn_defs)

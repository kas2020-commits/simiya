import typing as t
from collections import abc

from simiya import datatypes as tt


def fetch_named_type(
    current_fn: tt.FnDefAst,
    argname: tt.VarName,
    resolved_types: abc.Mapping[tt.VarName, tt.TypedNamedExpression],
) -> tt.NamedType:
    """Fetch a named type for type-checking purposes."""
    match current_fn.namespace[argname]:
        case tt.NodeT.ACN:
            return current_fn.acns[argname]
        case tt.NodeT.ICN:
            if argname not in resolved_types:
                raise ValueError(f"Variable {argname} Used before definition")
            currarg_type = resolved_types[argname]
            return tt.NamedType(name=argname, type_=currarg_type.type_)
        case tt.NodeT.TCN:
            raise ValueError(
                "You somehow refered to the terminal expression "
                "in the body, please don't do that..."
            )


def hm_sub_def(
    invoked_fn: tt.FnDefAst,
    expr: tt.Expression,
    currexpr_env: abc.Iterable[tt.NamedType],
    current_fn: tt.FnDefAst,
) -> tt.TensorType:
    constraints: dict[tt.ConstraintRef, tt.ConstraintRef] = {}

    if len(invoked_fn.acns) != len(expr.nodes):
        raise ValueError(
            f"Incorrect number of arguments provided to {invoked_fn.symbol}: "
            f"expected {len(invoked_fn.acns)}, got {len(expr.nodes)}"
        )

    for (invoked_arg_name, invoked_arg), currarg in zip(
        invoked_fn.acns.items(), currexpr_env
    ):
        if len(invoked_arg.type_.ranks) != len(currarg.type_.ranks):
            raise ValueError(
                f"Mismatching ranks between "
                f"{invoked_arg=} and {currarg=} "
                f"in {current_fn.symbol}"
            )
        constraints[invoked_arg_name] = currarg.name

        for invoked_arg_rank, currarg_rank in zip(
            invoked_arg.type_.ranks, currarg.type_.ranks
        ):
            constraints[invoked_arg_rank] = currarg_rank

        constraints[invoked_arg.type_.field] = currarg.type_.field

    subbed_type = tt.TensorType(
        t.cast(
            tt.VarName | tt.ConcreteField,
            constraints[invoked_fn.tcn.type_.field],
        ),
        tuple(constraints[rank] for rank in invoked_fn.tcn.type_.ranks),
    )

    return subbed_type


def hm_sub_decl(
    invoked_fn: tt.FnDeclAst,
    expr: tt.Expression,
    currexpr_env: abc.Iterable[tt.NamedType],
    current_fn: tt.FnDefAst,
) -> tt.TensorType:
    constraints: dict[tt.ConstraintRef, tt.ConstraintRef] = {}

    if len(invoked_fn.acns) != len(expr.nodes):
        raise ValueError(
            f"Incorrect number of arguments provided to {invoked_fn.symbol}: "
            f"expected {len(invoked_fn.acns)}, got {len(expr.nodes)}"
        )

    for invoked_arg, currexpr_arg in zip(
        invoked_fn.acns.values(), currexpr_env
    ):
        if len(invoked_arg.type_.ranks) != len(currexpr_arg.type_.ranks):
            raise ValueError(
                f"Mismatching ranks between "
                f"{invoked_arg=} and {currexpr_arg=} "
                f"in {current_fn.symbol}"
            )
        constraints[invoked_arg.name] = currexpr_arg.name
        for invoked_arg_rank, currarg_rank in zip(
            invoked_arg.type_.ranks, currexpr_arg.type_.ranks
        ):
            constraints[invoked_arg_rank] = currarg_rank
        constraints[invoked_arg.type_.field] = currexpr_arg.type_.field

    subbed_type = tt.TensorType(
        t.cast(
            tt.VarName | tt.ConcreteField,
            constraints[invoked_fn.ret.field],
        ),
        tuple(constraints[rank] for rank in invoked_fn.ret.ranks),
    )

    return subbed_type


def hm_expr_type(
    mod: tt.Module,
    current_fn: tt.FnDefAst,
    expr: tt.Expression,
    checked_defs: abc.Set[tt.Binding],
    resolved_types: abc.Mapping[tt.VarName, tt.TypedNamedExpression],
) -> tt.TensorType:
    """Resolve the type annotation for a given expression.

    This function uses the Hindley-Milner type deduction family of algorithms
    to perform type substitution iteratively until all required types have been
    resolved.
    """
    is_checked_fn_def = expr.fn_symbol in checked_defs
    is_fn_decl = expr.fn_symbol in mod.fn_decls
    if not (is_checked_fn_def or is_fn_decl):
        raise ValueError(
            f"Cannot invoke function {expr.fn_symbol} " "before definition"
        )
    invoked_fn = (
        mod.fn_decls[expr.fn_symbol]
        if is_fn_decl
        else mod.fn_defs[expr.fn_symbol]
    )
    currexpr_env = tuple(
        fetch_named_type(current_fn, argname, resolved_types)
        for argname in expr.nodes
    )
    match invoked_fn:
        case tt.FnDefAst():
            return hm_sub_def(invoked_fn, expr, currexpr_env, current_fn)
        case tt.FnDeclAst():
            return hm_sub_decl(invoked_fn, expr, currexpr_env, current_fn)


def resolve_fn_types(
    mod: tt.Module, fn: tt.FnDefAst, checked_defs: abc.Set[tt.Binding]
) -> abc.Mapping[tt.VarName, tt.TypedNamedExpression]:
    """Iteratively resolve all expression types in a function.

    Returns:
        Collection of all expressions typed, indexed by their binding symbol.
    """
    resolved_types: dict[tt.VarName, tt.TypedNamedExpression] = {}

    # Perform substitution on ICNS
    for icn_name, expr in fn.icns.items():
        icn_type = hm_expr_type(
            mod,
            fn,
            expr,
            checked_defs,
            resolved_types,
        )
        resolved_types[icn_name] = tt.TypedNamedExpression(
            name=icn_name, value=expr, type_=icn_type
        )

    # Perform substitution on TCN
    infered_ret_type = hm_expr_type(
        mod, fn, fn.tcn.value, checked_defs, resolved_types
    )
    if infered_ret_type != fn.tcn.type_:
        raise ValueError(
            f"Type Error: Expected {fn.tcn.type_}, got {infered_ret_type}"
        )

    return resolved_types

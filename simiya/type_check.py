import networkx as nx
import typing as t

from . import types as tt
from rich import print


def get_new_varname(
    fn_namespace: tt.LocalNamespace
    | tuple[tt.VarName, ...]
    | set[tt.VarName]
    | frozenset[tt.VarName],
) -> tt.VarName:
    for candidate_varname in tt.VarName:
        if candidate_varname in fn_namespace:
            continue
        else:
            return candidate_varname
    raise ValueError("Ran out of local variable names!")


def fn_decl_to_ast(namespace: tt.ParsedNamespace, fn: tt.Fn) -> tt.FnDeclAst:
    return tt.FnDeclAst(
        symbol=fn.symbol, constraints=fn.constraints, args=fn.args, ret=fn.ret
    )


def fn_def_to_ast(namespace: tt.ParsedNamespace, fn: tt.Fn) -> tt.FnDefAst:
    compute_dag: nx.DiGraph[tt.VarName] = nx.DiGraph()
    fn_namespace: tt.LocalNamespace = {}

    if fn.body is None:
        raise ValueError("Only call this on functions with definitions")

    for compute_node in (*fn.args, *fn.body.inodes):
        if compute_node.name in fn_namespace:
            raise ValueError("Same variable defined multiple times")
        compute_dag.add_node(compute_node.name)

    for compute_node in fn.args:
        fn_namespace[compute_node.name] = tt.NodeT.ACN

    for compute_node in fn.body.inodes:
        fn_namespace[compute_node.name] = tt.NodeT.ICN

    for inode in fn.body.inodes:
        if inode.value is None:
            raise ValueError("Internal Node is missing its definition")

        if inode.value.fn_symbol not in namespace:
            raise ValueError(
                f"unknown symbol ({inode.value.fn_symbol} not in namespace)"
            )

        for dependent_node in inode.value.nodes:
            compute_dag.add_edge(dependent_node, inode.name)

    terminal_varname = get_new_varname(fn_namespace)

    fn_namespace[terminal_varname] = tt.NodeT.TCN

    terminal_node = tt.TerminalNode(
        name=terminal_varname, value=fn.body.terminal, annotation=fn.ret
    )

    for dependent_node in fn.body.terminal.nodes:
        compute_dag.add_edge(dependent_node, terminal_varname)

    return tt.FnDefAst(
        symbol=fn.symbol,
        constraints=fn.constraints,
        compute_dag=compute_dag,
        namespace=fn_namespace,
        icns={x.name: x.value for x in fn.body.inodes},
        tcn=terminal_node,
        acns={x.name: x.annotation for x in fn.args},
    )


###############################################################################


def fetch_icn_nodetype(
    current_fn: tt.FnDefAst,
    argname: tt.VarName,
    resolved_types: dict[tt.VarName, tt.TensorAnnotation],
) -> tt.ArgNode:
    match current_fn.namespace[argname]:
        case tt.NodeT.ACN:
            currarg_type = current_fn.acns[argname]
            return tt.ArgNode(argname, currarg_type)
        case tt.NodeT.ICN:
            if argname not in resolved_types:
                raise ValueError(f"Variable {argname} Used before definition")
            currarg_type = resolved_types[argname]
            return tt.ArgNode(argname, currarg_type)
        case tt.NodeT.TCN:
            raise ValueError(
                "You somehow refered to the terminal expression"
                "in the body, please don't do that..."
            )


def resolve_hm_substitution(
    mod: tt.Module,
    current_fn: tt.FnDefAst,
    expr: tt.Expression,
    checked_defs: set[tt.Symbol],
    resolved_types: dict[tt.VarName, tt.TensorAnnotation],
) -> tt.TensorAnnotation:
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
        fetch_icn_nodetype(current_fn, argname, resolved_types)
        for argname in expr.nodes
    )
    constraints: dict[tt.ConstraintRef, tt.ConstraintRef] = {}
    match invoked_fn:
        case tt.FnDefAst():
            if len(invoked_fn.acns) != len(expr.nodes):
                raise ValueError(
                    f"Incorrect number of arguments provided to {invoked_fn.symbol}: "
                    f"expected {len(invoked_fn.acns)}, got {len(expr.nodes)}"
                )
            for (invoked_arg_name, invoked_arg_type), currarg in zip(
                invoked_fn.acns.items(), currexpr_env
            ):
                if len(invoked_arg_type.ranks) != len(
                    currarg.annotation.ranks
                ):
                    raise ValueError(
                        f"Mismatching ranks between "
                        f"{invoked_arg_type=} and {currarg=} "
                        f"in {current_fn.symbol}"
                    )
                constraints[invoked_arg_name] = currarg.name
                for invoked_arg_rank, currarg_rank in zip(
                    invoked_arg_type.ranks, currarg.annotation.ranks
                ):
                    constraints[invoked_arg_rank] = currarg_rank
                constraints[invoked_arg_type.field] = currarg.annotation.field
            subbed_type = tt.TensorAnnotation(
                t.cast(
                    tt.VarName | tt.ConcreteField,
                    constraints[invoked_fn.tcn.annotation.field],
                ),
                t.cast(
                    tuple[tt.Rank, ...],
                    tuple(
                        constraints[rank]
                        for rank in invoked_fn.tcn.annotation.ranks
                    ),
                ),
            )
            return subbed_type
        case tt.FnDeclAst():
            if len(invoked_fn.args) != len(expr.nodes):
                raise ValueError(
                    f"Incorrect number of arguments provided to {invoked_fn.symbol}: "
                    f"expected {len(invoked_fn.args)}, got {len(expr.nodes)}"
                )

            for invoked_arg, currarg in zip(invoked_fn.args, currexpr_env):
                if len(invoked_arg.annotation.ranks) != len(
                    currarg.annotation.ranks
                ):
                    raise ValueError(
                        f"Mismatching ranks between "
                        f"{invoked_arg=} and {currarg=} "
                        f"in {current_fn.symbol}"
                    )
                constraints[invoked_arg.name] = currarg.name
                for invoked_arg_rank, currarg_rank in zip(
                    invoked_arg.annotation.ranks, currarg.annotation.ranks
                ):
                    constraints[invoked_arg_rank] = currarg_rank
                constraints[
                    invoked_arg.annotation.field
                ] = currarg.annotation.field

            subbed_type = tt.TensorAnnotation(
                t.cast(
                    tt.VarName | tt.ConcreteField,
                    constraints[invoked_fn.ret.field],
                ),
                t.cast(
                    tuple[tt.Rank, ...],
                    tuple(constraints[rank] for rank in invoked_fn.ret.ranks),
                ),
            )
            return subbed_type


def check_fn(
    mod: tt.Module, fn: tt.FnDefAst, checked_defs: set[tt.Symbol]
) -> dict[tt.VarName, tt.TensorAnnotation]:
    resolved_types: dict[tt.VarName, tt.TensorAnnotation] = {}
    for icn_name, expr in fn.icns.items():
        icn_annotation = resolve_hm_substitution(
            mod,
            fn,
            expr,
            checked_defs,
            resolved_types,
        )
        resolved_types[icn_name] = icn_annotation
    infered_ret_type = resolve_hm_substitution(
        mod, fn, fn.tcn.value, checked_defs, resolved_types
    )
    resolved_types[fn.tcn.name] = infered_ret_type
    if infered_ret_type != fn.tcn.annotation:
        raise ValueError(
            f"Type Error: Expected {fn.tcn.annotation}, got {infered_ret_type}"
        )
    return resolved_types


def check_module(mod: tt.Module):
    checked_defs: set[tt.Symbol] = set()
    for fn_symbol, fn_def_ast in mod.fn_defs.items():
        resolved_fn_types = check_fn(mod, fn_def_ast, checked_defs)
        print(resolved_fn_types)
        checked_defs.add(fn_symbol)

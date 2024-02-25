from simiya import datatypes as tt

from .function import resolve_fn_types


def typecheck_module(mod: tt.UntypedModule) -> tt.TypedModule:
    typed_fn_defs: dict[tt.Binding, tt.TypedFnDef] = {}
    for fn_symbol, fn_def_ast in mod.fn_defs.items():
        typed_exprs = resolve_fn_types(mod, fn_def_ast, typed_fn_defs.keys())
        typed_fn_defs[fn_symbol] = tt.TypedFnDef(
            symbol=fn_def_ast.symbol,
            constraints=fn_def_ast.constraints,
            namespace=fn_def_ast.namespace,
            icns=typed_exprs,
            ret=fn_def_ast.ret,
            acns=fn_def_ast.acns,
        )
    return tt.TypedModule(
        symbols=mod.symbols,
        sum_types=mod.sum_types,
        fn_decls=mod.fn_decls,
        fn_defs=typed_fn_defs,
    )

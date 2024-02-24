from rich import print

from simiya import datatypes as tt

from .functions import check_fn


def check_module(mod: tt.Module):
    checked_defs: set[tt.Symbol] = set()
    for fn_symbol, fn_def_ast in mod.fn_defs.items():
        resolved_fn_types = check_fn(mod, fn_def_ast, checked_defs)
        print(resolved_fn_types)
        checked_defs.add(fn_symbol)

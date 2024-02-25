from simiya import datatypes as tt

from . import grammar, transform


def lower_prog(prog: str) -> tt.UntypedModule:
    parser = grammar.gen_parser()
    tree = parser.parse(prog)
    mod = transform.ast_convert(tree)
    return mod

import click

from .ast import parse_start

from . import grammar


@click.group
def main():
    ...


@main.command
def test():
    parser = grammar.gen_parser()

    prog = r"""
field Float := f8 | f16 | f32 | f64;
field Int := i8 | i16 | i32 | i64;
field T := Float;

prop matmul {a : Float} :: (x : [m][n]a) (y : [n][k]a) -> [m][k]a;
prop iota :: (n : Int) -> [n]Float;
prop id :: (x : a) -> a;
prop base_value :: Float;
prop tensor_value :: [m][n][k][10]T;
    """

    tree = parser.parse(prog)

    breakpoint()

    # ast = traverse_tree(parse_tree)

    ast = parse_start(tree)

    breakpoint()

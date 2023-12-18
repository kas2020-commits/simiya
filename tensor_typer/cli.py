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
type Float := f8 | f16 | f32 | f64;
type Int := i8 | i16 | i32 | i64;

prop matmul {a : Float} :: (x : [m][n]a) (y : [n][k]a) -> [m][k]a;
prop iota :: (n : Int) -> [n]i32;
prop id :: (x: a) -> a
prop baseValue :: Float;
    """

    parse_tree = parser.parse(prog)

    breakpoint()

    # ast = traverse_tree(parse_tree)

    ast = parse_start(parse_tree)

    breakpoint()

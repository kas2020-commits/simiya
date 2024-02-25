import typing as t

import rich
import typer

from .frontend import lower_prog
from .type_system.module import typecheck_module

App = typer.Typer(help="Typer")

PROG: t.Final = r"""
field Float := f8|f16|f32|f64;
field Int := i8|i16|i32|i64;

fn basic (x: [k][10]i32) -> k;
fn len (x: [n]a) -> n;
fn add (x: t, y: t) -> t;
fn <z Float> matmul (x: [a][b]z, y: [b][c]z) -> [a][c]z;

fn <t Float> matmul2 (x: [m][n]t, y: [n][k]t, z: [k][j]t) -> [m][j]t {
    let
        a := matmul x y;
    in
        matmul a z
}

fn <t Float> matmul3 (w: [h][j]t, x: [j][m]t, y: [m][n]t, z: [n][k]t) -> [h][k]t {
    let
        a := matmul w x;
        b := matmul a y;
    in
        matmul b z
}

fn <t Float> matmul3_alt (w: [h][j]t, x: [j][m]t, y: [m][n]t, z: [n][k]t) -> [h][k]t {
    let
        a := matmul2 w x y;
    in
        matmul a z
}
    """


@App.command()
def test():
    mod = lower_prog(PROG)
    typechecked_mod = typecheck_module(mod)
    rich.print(typechecked_mod)

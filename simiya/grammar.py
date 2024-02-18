"""Defines the grammar.
"""

import typing as t

import lark

DEFAULT_GRAMMAR: t.Final = r"""
start: | (user_field|function)+

user_field: "field" TYPE_SYMBOL ":=" fieldclass ";" -> user_field
function: "fn" local_constraints SYMBOL fn_input "->" annotation fn_body -> fn

fn_body: (";"|"{" (("let" internal_nodes "in" expr)|expr) "}")

internal_nodes: internal_node+ -> inodes
internal_node: VARNAME ":=" expr ";" -> inode

expr: SYMBOL VARNAME+

local_constraints: ("<" local_constraint ("," local_constraint)*  ">")? -> constraints
local_constraint: VARNAME fieldclass -> constraint

fn_input: "(" arg ("," arg)* ")" -> args
arg: VARNAME ":" annotation -> arg

annotation: ("["(static_rank|bound_rank)"]")* (CONCRETE_FIELD|VARNAME) -> ret
fieldclass: CONCRETE_FIELD ("|" CONCRETE_FIELD)* -> fields

static_rank: INT
bound_rank: VARNAME

CONCRETE_FIELD: ATOMIC_FIELD|TYPE_SYMBOL

ATOMIC_FIELD: "i8" | "i16" | "i32" | "i64" | "f8" | "f16" | "f32" | "f64"
VARNAME: LCASE_LETTER
SYMBOL: LCASE_LETTER (LETTER|DIGIT|"_")+
TYPE_SYMBOL: UCASE_LETTER (LETTER|DIGIT)*

%import common.LCASE_LETTER
%import common.LETTER
%import common.UCASE_LETTER
%import common.DIGIT
%import common.WS
%import common.INT

%ignore WS
"""


def gen_parser(grammar: str = DEFAULT_GRAMMAR) -> lark.Lark:
    return lark.Lark(grammar)

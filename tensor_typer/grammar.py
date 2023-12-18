"""Defines the grammar.
"""

import typing as t

import lark

DEFAULT_GRAMMAR: t.Final = r"""
start: | ((field_def|prop) ";")+

field_def: "field" _type_symbol ":=" fieldclass -> user_field
prop: "prop" _prop_symbol local_constraints "::" prop_args general_type -> prop

local_constraints: local_constraint* -> constraints
local_constraint: "{" _var ":" fieldclass "}" -> constraint

prop_args: [arg+ "->"] -> args
arg: "(" _var ":" general_type ")" -> arg

general_type: _rank* (_concrete_field|_var) -> ret
fieldclass: _concrete_field ("|" _concrete_field)* -> fields

_rank: "[" (INT | _var) "]"
_concrete_field: _atomic_field|_type_symbol
!_atomic_field: "i8" | "i16" | "i32" | "i64" | "f8" | "f16" | "f32" | "f64"
_var: LCASE_LETTER
_prop_symbol: /[abcdefghijklmnopqrstuvwxyz]+[abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'_']+/
_type_symbol: /[ABCDEFGHIJKLMNOPQRSTUVWXYZ]+[abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789]*/

%import common.LCASE_LETTER
%import common.WS
%import common.INT

%ignore WS
"""


def gen_parser(grammar: str = DEFAULT_GRAMMAR) -> lark.Lark:
    return lark.Lark(grammar)

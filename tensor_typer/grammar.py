"""Defines the grammar.
"""

import typing as t

import lark

DEFAULT_GRAMMAR: t.Final = r"""
start: | ( prop | alias )+

prop: "prop" prop_symbol type_constraint* "::" ((arg+ "->" general_type) | general_type) ";"
alias: "type" alias_symbol ":=" concrete_type ("|" concrete_type)* ";"

alias_symbol: UCASE_LETTER (LETTER|DIGIT)*
prop_symbol: LCASE_LETTER (LETTER|DIGIT)+

type_constraint: "{" var ":" concrete_type ("," concrete_type)* "}"
arg: "(" var ":" general_type ")"

general_type: concrete_type | (rank* var)
concrete_type: rank* (atomic_type|alias_symbol)
rank: "[" (INT | var) "]"
atomic_type: i8 | i16 | i32 | i64 | f8 | f16 | f32 | f64

i8: "i8"
i16: "i16"
i32: "i32"
i64: "i64"
f8: "f8"
f16: "f16"
f32: "f32"
f64: "f64"

var: LCASE_LETTER

%import common.WORD
%import common.LETTER
%import common.DIGIT
%import common.LCASE_LETTER
%import common.UCASE_LETTER
%import common.CNAME
%import common.WS
%import common.INT

%ignore WS
"""


def gen_parser(grammar: str = DEFAULT_GRAMMAR) -> lark.Lark:
    return lark.Lark(grammar)

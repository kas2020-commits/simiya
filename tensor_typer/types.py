import enum
import typing as t
from dataclasses import dataclass


class Var(enum.StrEnum):
    LETTER_A = "a"
    LETTER_B = "b"
    LETTER_C = "c"
    LETTER_D = "d"
    LETTER_E = "e"
    LETTER_F = "f"
    LETTER_G = "g"
    LETTER_H = "h"
    LETTER_I = "i"
    LETTER_J = "j"
    LETTER_K = "k"
    LETTER_L = "l"
    LETTER_M = "m"
    LETTER_N = "n"
    LETTER_O = "o"
    LETTER_P = "p"
    LETTER_Q = "q"
    LETTER_R = "r"
    LETTER_S = "s"
    LETTER_T = "t"
    LETTER_U = "u"
    LETTER_V = "v"
    LETTER_W = "w"
    LETTER_X = "x"
    LETTER_Y = "y"
    LETTER_Z = "z"


class Field(enum.StrEnum):
    i8 = enum.auto()
    i16 = enum.auto()
    i32 = enum.auto()
    i64 = enum.auto()
    u8 = enum.auto()
    u16 = enum.auto()
    u32 = enum.auto()
    u64 = enum.auto()
    f8 = enum.auto()
    f16 = enum.auto()
    f32 = enum.auto()
    f64 = enum.auto()


Symbol: t.TypeAlias = str


@dataclass(slots=True, frozen=True)
class GeneralType:
    field: Var | Field
    ranks: tuple[Var | int, ...]


@dataclass(slots=True, frozen=True)
class Arg:
    var: Var
    typeclass: GeneralType


@dataclass(slots=True, frozen=True)
class TypeConstraint:
    var: Var
    typeclasses: frozenset[GeneralType]


@dataclass(slots=True, frozen=True)
class Alias:
    symbol: Symbol
    typeclasses: frozenset[Field]


@dataclass(slots=True, frozen=True)
class Decl:
    symbol: Symbol
    ret: GeneralType
    args: tuple[Arg, ...]


Namespace: t.TypeAlias = dict[Symbol, Decl | Alias]

import enum
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


class AtomicField(enum.StrEnum):
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


type Symbol = str
type FieldClassSymbol = str
type Rank = int | Var
type ConcreteField = AtomicField | FieldClassSymbol
type FieldClass = frozenset[ConcreteField]


@dataclass(slots=True, frozen=True)
class GeneralType:
    field: Var | ConcreteField
    ranks: tuple[Rank, ...]


@dataclass(slots=True, frozen=True)
class Arg:
    var: Var
    ret: GeneralType


@dataclass(slots=True, frozen=True)
class Constraint[T: Var | Symbol]:
    binding: T
    group: FieldClass


type LocalConstraint = Constraint[Var]
type ModuleConstraint = Constraint[Symbol]


@dataclass(slots=True, frozen=True)
class Prop:
    symbol: Symbol
    ret: GeneralType
    args: tuple[Arg, ...]
    constraints: tuple[LocalConstraint, ...]


type Namespace = dict[Symbol, Prop | ModuleConstraint]

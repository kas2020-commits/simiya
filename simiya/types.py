import enum
from dataclasses import dataclass
from types import NoneType as NULL

import networkx as nx


class VarName(enum.StrEnum):
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


class NodeT(enum.Enum):
    ACN = enum.auto()
    ICN = enum.auto()
    TCN = enum.auto()


class ModScopeT(enum.Enum):
    FN_DECL = enum.auto()
    FN_DEF = enum.auto()
    SUM_TYPE = enum.auto()


type Symbol = str
type FieldClassSymbol = str
type Rank = int | VarName
type ConcreteField = AtomicField | FieldClassSymbol
type FieldClass = frozenset[ConcreteField]

type ConstraintRef = VarName | Rank | ConcreteField


@dataclass(slots=True, frozen=True)
class TensorAnnotation:
    field: VarName | ConcreteField
    ranks: tuple[Rank, ...]

    def __str__(self):
        return (
            f"{"".join(f"[{rank}]" for rank in self.ranks)}{str(self.field)}"
        )


@dataclass(slots=True, frozen=True)
class SumType[T: VarName | Symbol]:
    symbol: T
    group: FieldClass


type LocalSumType = SumType[VarName]
type GlobalSumType = SumType[Symbol]


@dataclass(slots=True, frozen=True)
class Expression:
    fn_symbol: Symbol
    nodes: tuple[VarName, ...]


@dataclass(slots=True, frozen=True)
class InternalNode:
    name: VarName
    value: Expression


@dataclass(slots=True, frozen=True)
class TerminalNode:
    name: VarName
    value: Expression
    annotation: TensorAnnotation


@dataclass(slots=True, frozen=True)
class ArgNode:
    name: VarName
    annotation: TensorAnnotation


@dataclass(slots=True, frozen=True)
class FnBody:
    inodes: tuple[InternalNode, ...]
    terminal: Expression


@dataclass(slots=True, frozen=True)
class Fn:
    symbol: Symbol
    constraints: frozenset[LocalSumType]
    args: tuple[ArgNode, ...]
    ret: TensorAnnotation
    body: FnBody | None


type ParsedNamespace = dict[Symbol, Fn | GlobalSumType]
type LocalNamespace = dict[VarName, NodeT]


@dataclass(slots=True, frozen=True)
class FnDeclAst:
    symbol: Symbol
    constraints: frozenset[LocalSumType]
    args: tuple[ArgNode, ...]
    ret: TensorAnnotation


@dataclass(slots=True, frozen=True)
class FnDefAst:
    symbol: Symbol
    constraints: frozenset[LocalSumType]
    compute_dag: nx.DiGraph
    namespace: LocalNamespace
    icns: dict[VarName, Expression]
    tcn: TerminalNode
    acns: dict[VarName, TensorAnnotation]


type FnDefNamespace = dict[Symbol, FnDefAst]
type FnDeclNamespace = dict[Symbol, FnDeclAst]
type SumTypeNamespace = dict[Symbol, GlobalSumType]
type SymbolNamespace = dict[Symbol, ModScopeT]


@dataclass(slots=True, frozen=True)
class Module:
    symbols: SymbolNamespace
    sum_types: SumTypeNamespace
    fn_decls: FnDeclNamespace
    fn_defs: FnDefNamespace

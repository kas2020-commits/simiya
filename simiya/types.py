import enum
import typing as t
from dataclasses import dataclass

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


Symbol: t.TypeAlias = str
FieldClassSymbol: t.TypeAlias = str
Rank: t.TypeAlias = int | VarName
ConcreteField: t.TypeAlias = AtomicField | FieldClassSymbol
FieldClass: t.TypeAlias = frozenset[ConcreteField]
ConstraintRef: t.TypeAlias = VarName | Rank | ConcreteField


@dataclass(slots=True, frozen=True)
class TensorAnnotation:
    field: VarName | ConcreteField
    ranks: tuple[Rank, ...]

    def __str__(self):
        ranks_str = "".join(f"[{rank}]" for rank in self.ranks)
        return f"{ranks_str}{str(self.field)}"


_T = t.TypeVar("_T", VarName, Symbol)


@dataclass(slots=True, frozen=True)
class SumType(t.Generic[_T]):
    symbol: _T
    group: FieldClass


LocalSumType: t.TypeAlias = SumType[VarName]
GlobalSumType: t.TypeAlias = SumType[Symbol]


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


ParsedNamespace: t.TypeAlias = dict[Symbol, Fn | GlobalSumType]
LocalNamespace: t.TypeAlias = dict[VarName, NodeT]


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


FnDefNamespace: t.TypeAlias = dict[Symbol, FnDefAst]
FnDeclNamespace: t.TypeAlias = dict[Symbol, FnDeclAst]
SumTypeNamespace: t.TypeAlias = dict[Symbol, GlobalSumType]
SymbolNamespace: t.TypeAlias = dict[Symbol, ModScopeT]


@dataclass(slots=True, frozen=True)
class Module:
    symbols: SymbolNamespace
    sum_types: SumTypeNamespace
    fn_decls: FnDeclNamespace
    fn_defs: FnDefNamespace

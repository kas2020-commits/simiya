import enum
import typing as t
from collections import abc
from dataclasses import dataclass


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


Binding: t.TypeAlias = str
FieldClassSymbol: t.TypeAlias = str
Rank: t.TypeAlias = int | VarName
ConcreteField: t.TypeAlias = AtomicField | FieldClassSymbol
FieldClass: t.TypeAlias = abc.Set[ConcreteField]
ConstraintRef: t.TypeAlias = VarName | Rank | ConcreteField


@dataclass(slots=True, frozen=True)
class TensorType:
    field: VarName | ConcreteField
    ranks: abc.Sequence[ConstraintRef]

    def __str__(self):
        ranks_str = "".join(f"[{rank}]" for rank in self.ranks)
        return f"{ranks_str}{str(self.field)}"


_Symbol = t.TypeVar("_Symbol", VarName, Binding)


@dataclass(slots=True, frozen=True)
class SumType(t.Generic[_Symbol]):
    symbol: _Symbol
    group: FieldClass


LocalSumType: t.TypeAlias = SumType[VarName]
GlobalSumType: t.TypeAlias = SumType[Binding]


@dataclass(slots=True, frozen=True)
class Expression:
    fn_symbol: Binding
    nodes: tuple[VarName, ...]


@dataclass(slots=True, frozen=True)
class NamedExpression:
    name: VarName
    value: Expression


@dataclass(slots=True, frozen=True)
class TypedNamedExpression:
    name: VarName
    value: Expression
    type_: TensorType


@dataclass(slots=True, frozen=True)
class NamedType:
    name: VarName
    type_: TensorType


@dataclass(slots=True, frozen=True)
class FnBody:
    inodes: tuple[NamedExpression, ...]
    terminal: Expression


@dataclass(slots=True, frozen=True)
class Fn:
    symbol: Binding
    constraints: abc.Set[LocalSumType]
    args: tuple[NamedType, ...]
    ret: TensorType
    body: FnBody | None


ParsedNamespace: t.TypeAlias = dict[Binding, Fn | GlobalSumType]
LocalNamespace: t.TypeAlias = dict[VarName, NodeT]


@dataclass(slots=True, frozen=True)
class FnDeclAst:
    symbol: Binding
    constraints: abc.Set[LocalSumType]
    acns: abc.Mapping[VarName, NamedType]
    ret: TensorType


@dataclass(slots=True, frozen=True)
class FnDefAst:
    symbol: Binding
    constraints: abc.Set[LocalSumType]
    namespace: LocalNamespace
    icns: abc.Mapping[VarName, Expression]
    tcn: TypedNamedExpression
    acns: abc.Mapping[VarName, NamedType]


@dataclass(slots=True, frozen=True)
class TypedFnDef:
    symbol: Binding
    constraints: abc.Set[LocalSumType]
    namespace: LocalNamespace
    icns: abc.Mapping[VarName, TypedNamedExpression]
    tcn: TypedNamedExpression
    acns: abc.Mapping[VarName, NamedType]


FnDefNamespace: t.TypeAlias = abc.Mapping[Binding, FnDefAst]
TypedFnDefNamespace: t.TypeAlias = abc.Mapping[Binding, TypedFnDef]
FnDeclNamespace: t.TypeAlias = abc.Mapping[Binding, FnDeclAst]
SumTypeNamespace: t.TypeAlias = abc.Mapping[Binding, GlobalSumType]
SymbolNamespace: t.TypeAlias = abc.Mapping[Binding, ModScopeT]


@dataclass(slots=True, frozen=True)
class Module:
    symbols: SymbolNamespace
    sum_types: SumTypeNamespace
    fn_decls: FnDeclNamespace
    fn_defs: FnDefNamespace


@dataclass(slots=True, frozen=True)
class TypedModule:
    symbols: SymbolNamespace
    sum_types: SumTypeNamespace
    fn_decls: FnDeclNamespace
    fn_defs: TypedFnDefNamespace

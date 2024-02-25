from dataclasses import dataclass

from ..datatypes import Expression, NamedExpression


@dataclass(slots=True, frozen=True)
class FnBody:
    inodes: tuple[NamedExpression, ...]
    terminal: Expression

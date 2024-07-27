from sqlite3 import Row
from typing import overload

TupleType = tuple[str, int, float | int, str, dict]
DataType = TupleType | Row
ValueType = str | int | float | dict
DictTypes = dict[str, str | int | float | dict[int, ... | ...]] | dict[str, str | int | float | ...] | dict[str, ...]
ListDictTypes = list[DictTypes]


def create_table() -> None:
    pass


def delete_table() -> None:
    pass


def add_one(symbol: str, z: int, mass: float | int, name: str, properties: dict) -> None:
    pass


def add_list(elemnet_list: ListDictTypes) -> None:
    pass


@overload
def get(symbol: str) -> TupleType | None:
    pass


@overload
def get(symbol: str, asrow: bool) -> DataType | None:
    pass


def get_all() -> list[TupleType]:
    pass


def update_one(element: DictTypes) -> None:
    pass


def update_list(elemnet_list: ListDictTypes) -> None:
    pass


def fetch_as_dict() -> dict[str, dict[str, ValueType]]:
    pass

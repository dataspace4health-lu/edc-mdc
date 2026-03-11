from sqlalchemy.orm import Session
from fastapi import Depends
from typing import TypeVar, Callable, Set, Type, Annotated, Tuple
from dependencies.database import get_db_session

T = TypeVar("T")


class EnumValuesService:
    def __init__(self, db_session: Annotated[Session, Depends(get_db_session)]):
        self._db_session = db_session

    def persist_enum_values(
        self,
        entity_update_strategy: Callable[[T], None],
        existing_enum_values: Set[T],
        dto_values: Set[str],
        clazz: Type[T],
    ) -> None:
        parsed_enum_values = set([clazz(key=it) for it in dto_values])

        to_create, to_delete = self._find_to_create_and_to_delete(
            parsed_enum_values, existing_enum_values
        )

        for enum_value in to_create:
            entity_update_strategy(enum_value)
            self._db_session.add(enum_value)

        for enum_value in to_delete:
            self._db_session.delete(enum_value)

    def _find_to_create_and_to_delete(
        self, new_values: Set[T], existing_values: Set[T]
    ) -> Tuple[Set[T], Set[T]]:
        to_create = set()

        for new_value in new_values:
            if new_value not in existing_values:
                to_create.add(new_value)

        to_delete = set()
        for existing_value in existing_values:
            if not existing_value in new_values:
                to_delete.add(existing_value)

        return (to_create, to_delete)

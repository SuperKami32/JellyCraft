from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class InMemoryDB:
    """Temporary repository abstraction until SQLite/Postgres is wired in."""

    tables: dict[str, list[dict[str, Any]]] = field(default_factory=dict)

    def get_table(self, table_name: str) -> list[dict[str, Any]]:
        return self.tables.setdefault(table_name, [])


db = InMemoryDB()

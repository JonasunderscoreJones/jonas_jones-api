from enum import Enum

class ForeignKey():
    table_name = None
    foreign_key = None

    def __init__(self, table_name: str, column_name: str):
        self.table_name = table_name
        self.column_name = column_name

    def get(self):
        return self.table_name, self.column_name

    def __str__(self):
        return f"{self.table_name} {self.column_name}"

    def __repr__(self):
        return f"{self.table_name}.{self.column_name}"


class ColumnType(Enum):
    VARCHAR = "VARCHAR"
    TEXT = "TEXT"
    INTEGER = "INTEGER"
    BIGINT = "BIGINT"
    DATE = "DATE"
    TIMESTAMP = "TIMESTAMP"
    TIMESTAMPTZ = "TIMESTAMP WITH TIME ZONE"
    BOOLEAN = "BOOLEAN"
    JSONB = "JSONB"
    UUID = "UUID"

    def sql(self, length=None):
        if self is ColumnType.VARCHAR:
            if length is not None:
                return f"VARCHAR({int(length)})"
            return "VARCHAR"
        return self.value


class ColumnBuilder:
    column_type = None
    length = None
    not_null = False
    unique = False
    default_value = None
    foreign_key = None

    def __init__(self, column_type: ColumnType = ColumnType.VARCHAR):
        self.column_type = column_type

    def set_column_type(self, column_type: ColumnType):
        self.column_type = column_type
        return self

    def set_length(self, length: int):
        self.length = length
        return self

    def set_not_null(self, not_null: bool):
        self.not_null = not_null
        return self

    def set_unique(self, unique: bool):
        self.unique = unique
        return self

    def set_default_value(self, default_value: str):
        self.default_value = default_value
        return self

    def set_foreign_key(self, foreign_key: ForeignKey):
        self.foreign_key = foreign_key
        return self

    def build(self) -> dict:
        return {
            "type": self.column_type,
            "length": self.length,
            "not_null": self.not_null,
            "unique": self.unique,
            "default": self.default_value,
            "fk": self.foreign_key.get() if self.foreign_key else None
        }


class TableBuilder():
    columns: dict = {}
    def __init__(self):
        pass

    def add_column(self, name, column_type: ColumnType = ColumnType.VARCHAR, length: int = 255, not_null: bool = False, unique: bool = False, default_value: str = None, foreign_key: ForeignKey = None):
        self.columns[name] = ColumnBuilder(column_type=column_type).set_length(length).set_not_null(not_null).set_unique(unique).set_default_value(default_value).set_foreign_key(foreign_key).build()
        return self

    def build(self):
        return self.columns
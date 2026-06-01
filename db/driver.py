import os
import re
import time

import psycopg2
from dotenv import load_dotenv
from psycopg2 import sql

from db.db_builders import TableBuilder, ColumnType, ForeignKey


class PostgresDriver:
    conn = None
    cur = None
    db_version = None

    def __init__(self):
        try:
            load_dotenv()

            while self.conn is None:
                try:
                    self.conn = psycopg2.connect(
                        dbname=os.getenv("DB_NAME"),
                        user=os.getenv("DB_USER"),
                        password=os.getenv("DB_PASSWORD"),
                        host=os.getenv("DB_HOST"),
                        port=os.getenv("DB_PORT"),
                    )
                except Exception as e:
                    print("Failed to initialize Postgres driver")
                    print(f"Exception: {e}")
                    print("Waiting and retrying...")
                    time.sleep(5)

            self.cur = self.conn.cursor()

            print('PostgreSQL database connected!')
            self.cur.execute('SELECT version()')

            self.db_version = self.cur.fetchone()
            print(f"Postgres Version: {self.db_version}")

            self.cur.close()

            # create tables using tuple-style specs (first column must be the primary key and must end with _ID)
            # self.create_table_if_not_exists(
            #     "int_pip_pipelines",
            #     {
            #         "ipp_id": (ColumnType.UUID,),
            #         "ipp_display_name": {"type": ColumnType.VARCHAR, "length": 255, "not_null": True},
            #         "ipp_create_date": {"type": ColumnType.DATE, "not_null": True},
            #     },
            # )
            self.create_table_if_not_exists(
                "int_pip_pipelines",
                TableBuilder()
                .add_column("ipp_id", column_type=ColumnType.UUID, not_null=True, unique=True)
                .add_column("ipp_display_name", column_type=ColumnType.VARCHAR, length=255, not_null=True, unique=True)
                .add_column("ipp_create_date", column_type=ColumnType.DATE, not_null=True)
                .build()
            )

            # self.create_table_if_not_exists(
            #     "int_pip_runs",
            #     {
            #         "ipr_id": (ColumnType.UUID,),
            #         "ipr_ipp_id": {"type": ColumnType.UUID, "not_null": True, "fk": ("int_pip_pipelines", "ipp_id")},
            #         "ipr_star_date": {"type": ColumnType.DATE, "not_null": True},
            #         "ipr_end_date": {"type": ColumnType.DATE},
            #         "ipr_data_count": {"type": ColumnType.INTEGER, "not_null": True},
            #     },
            # )
            self.create_table_if_not_exists(
                "int_pip_runs",
                TableBuilder()
                .add_column("ipr_id", column_type=ColumnType.UUID, not_null=True, unique=True)
                .add_column("ipr_ipp_id", column_type=ColumnType.UUID, not_null=True, foreign_key=ForeignKey("int_pip_pipelines", "ipp_id"))
                .add_column("ipr_star_date", column_type=ColumnType.DATE, not_null=True)
                .add_column("ipr_end_date", column_type=ColumnType.DATE)
                .add_column("ipr_data_count", column_type=ColumnType.INTEGER, not_null=True)
                .build()
            )

            # self.create_table_if_not_exists(
            #     "int_req_requests",
            #     {
            #         "irr_id": (ColumnType.UUID,),
            #         "irr_endpoint": {"type": ColumnType.VARCHAR, "length": 2000, "not_null": True},
            #         "irr_method": {"type": ColumnType.VARCHAR, "length": 10, "not_null": True},
            #         "irr_status_code": {"type": ColumnType.INTEGER, "not_null": True},
            #         "irr_request_date": {"type": ColumnType.DATE, "not_null": True},
            #     },
            # )
            self.create_table_if_not_exists(
                "int_req_requests",
                TableBuilder()
                .add_column("irr_id", column_type=ColumnType.UUID, not_null=True, unique=True)
                .add_column("irr_endpoint", column_type=ColumnType.VARCHAR, length=2000, not_null=True)
                .add_column("irr_method", column_type=ColumnType.VARCHAR, length=10, not_null=True)
                .add_column("irr_status_code", column_type=ColumnType.INTEGER, not_null=True)
                .add_column("irr_request_date", column_type=ColumnType.DATE, not_null=True)
                .build()
            )

            # self.create_table_if_not_exists("kcomebacks", {}) //TODO figure out of one table is enough and how to store the data from json in table. maybe separate artists to own table? maybe release type? maybe links?

        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if self.conn is not None:
                self.conn.close()
                print('Database connection closed.')

    def create_table_if_not_exists(self, table_name: str, columns: dict):
        # check for valid table name to prevent SQL injection
        if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", table_name):
            raise ValueError("Invalid table name")
        # try to create pgcrypto extension so we can default id to gen_random_uuid(); ignore failures
        with self.conn.cursor() as cur:
            try:
                cur.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto";')
                self.conn.commit()
                pgcrypto_available = True
            except Exception:
                # creating extensions may require superuser; we'll continue without default UUID generation
                self.conn.rollback()
                pgcrypto_available = False

        # Determine primary key: use the first column in the provided dict.
        # It MUST end with _ID (per project convention); otherwise raise an error.
        try:
            pk_col = next(iter(columns.keys()))
        except StopIteration:
            raise ValueError("columns dict must define at least one column to serve as primary key")

        if not pk_col.upper().endswith('_ID'):
            raise ValueError("The first column must be a primary key and must end with '_ID'")

        # build column SQL fragments
        col_fragments = []
        fk_constraints = []  # collect foreign key constraints for later

        for col_name, col_spec in columns.items():
            # validate column name
            if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", col_name):
                raise ValueError(f"Invalid column name: {col_name}")

            # Handle the primary key column specially (first column, ending in _ID)
            is_pk = (col_name == pk_col)

            # Parse column spec (support dict, tuple, ColumnType, or string)
            not_null = False
            unique = False
            default = None
            fk_ref = None
            type_sql = None

            if isinstance(col_spec, dict):
                # Dict format: {"type": ColumnType, "length": 255, "not_null": True, "unique": False, "default": None, "fk": ("table", "col")}
                if "type" not in col_spec:
                    raise ValueError(f"Column {col_name} dict spec must include 'type' key")

                typ = col_spec["type"]
                length = col_spec.get("length")
                not_null = col_spec.get("not_null", False)
                unique = col_spec.get("unique", False)
                default = col_spec.get("default")
                fk_ref = col_spec.get("fk")  # tuple: (table_name, column_name)

                if isinstance(typ, ColumnType):
                    type_sql = typ.sql(length)
                elif isinstance(typ, str):
                    key = typ.upper()
                    if key in ColumnType.__members__:
                        type_sql = ColumnType[key].sql(length)
                    else:
                        raise ValueError(f"Unknown type: {typ}")
                else:
                    raise ValueError(f"Invalid column type for {col_name}: {typ}")

            elif isinstance(col_spec, tuple):
                # Handle both 1-element tuples (type only) and 2-element tuples (type + length)
                if len(col_spec) == 1:
                    typ = col_spec[0]
                    length = None
                elif len(col_spec) == 2:
                    typ, length = col_spec
                else:
                    raise ValueError(f"Invalid tuple spec for {col_name}: expected 1 or 2 elements, got {len(col_spec)}")

                if isinstance(typ, ColumnType):
                    type_sql = typ.sql(length)
                elif isinstance(typ, str):
                    key = typ.upper()
                    if key in ColumnType.__members__:
                        type_sql = ColumnType[key].sql(length)
                    else:
                        raise ValueError(f"Unknown type: {typ}")
                else:
                    raise ValueError(f"Invalid column type for {col_name}: {col_spec}")

            elif isinstance(col_spec, ColumnType):
                type_sql = col_spec.sql()
            elif isinstance(col_spec, str):
                # allow explicit type strings like VARCHAR(100) or simple names mapped to ColumnType
                if '(' in col_spec:
                    # basic sanitation: only allow letters, numbers, underscores, spaces, parentheses, and commas
                    if not re.match(r"^[A-Za-z0-9_\s\(\),]+$", col_spec):
                        raise ValueError(f"Invalid type string: {col_spec}")
                    type_sql = col_spec
                else:
                    key = col_spec.upper()
                    if key in ColumnType.__members__:
                        type_sql = ColumnType[key].sql()
                    else:
                        # last resort: basic sanitation
                        if not re.match(r"^[A-Za-z0-9_\s]+$", col_spec):
                            raise ValueError(f"Invalid type string: {col_spec}")
                        type_sql = col_spec
            else:
                raise ValueError(f"Invalid column spec for {col_name}: {col_spec}")

            # Build column definition
            col_def_parts = [sql.Identifier(col_name)]

            # For primary key column, force UUID type and add PRIMARY KEY constraint
            if is_pk:
                # Always UUID for primary key
                if pgcrypto_available:
                    col_def_parts.append(sql.SQL("UUID PRIMARY KEY DEFAULT gen_random_uuid()"))
                else:
                    col_def_parts.append(sql.SQL("UUID PRIMARY KEY"))
            else:
                # Non-PK column: type + constraints
                col_def_parts.append(sql.SQL(type_sql))

                if not_null:
                    col_def_parts.append(sql.SQL("NOT NULL"))

                if unique:
                    col_def_parts.append(sql.SQL("UNIQUE"))

                if default is not None:
                    if isinstance(default, str):
                        col_def_parts.append(sql.SQL("DEFAULT {}").format(sql.Literal(default)))
                    else:
                        col_def_parts.append(sql.SQL("DEFAULT {}").format(sql.Literal(str(default))))

                # Collect foreign key constraints (will be added after all columns)
                if fk_ref:
                    if not isinstance(fk_ref, (tuple, list)) or len(fk_ref) != 2:
                        raise ValueError(f"Foreign key for {col_name} must be a tuple (table_name, column_name)")
                    fk_table, fk_col = fk_ref
                    fk_constraints.append((col_name, fk_table, fk_col))

            col_def = sql.SQL(" ").join(col_def_parts)
            col_fragments.append(col_def)

        # Add foreign key constraints as separate clauses
        for fk_col, fk_table, fk_column in fk_constraints:
            fk_def = sql.Composed([
                sql.SQL("CONSTRAINT "),
                sql.Identifier(f"fk_{pk_col}_{fk_col}"),
                sql.SQL(" FOREIGN KEY ("),
                sql.Identifier(fk_col),
                sql.SQL(") REFERENCES "),
                sql.Identifier(fk_table),
                sql.SQL(" ("),
                sql.Identifier(fk_column),
                sql.SQL(")"),
            ])
            col_fragments.append(fk_def)

        full_columns_sql = sql.SQL(", ").join(col_fragments)

        create_query = sql.SQL("CREATE TABLE IF NOT EXISTS {} ({})").format(
            sql.Identifier(table_name),
            full_columns_sql
        )

        with self.conn.cursor() as cur:
            cur.execute(create_query)
            self.conn.commit()
            print(f"Table '{table_name}' created or already exists.")


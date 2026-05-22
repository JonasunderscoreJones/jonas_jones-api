import os
import re
import time

import psycopg2
from dotenv import load_dotenv
from psycopg2 import sql


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

            self.create_table_if_not_exists("INT_PIP_PIPELINES", {"IPP_ID": "VARCHAR", "IPP_DISPLAY_NAME": "VARCHAR", "IPP_CREATE_DATE": "DATE"})
            self.create_table_if_not_exists("INT_PIP_RUNS", {"IPR_ID": "VARCHAR", "IPR_IPP_ID": "VARCHAR", "IPR_START_DATE": "DATE", "IPR_END_DATE": "DATE", "IPR_DATA_COUNT": "INTEGER"})
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

        with self.conn.cursor() as cur:
            # Check whether the table exists
            cur.execute(
                """
                SELECT EXISTS (SELECT
                               FROM information_schema.tables
                               WHERE table_schema = 'public'
                                 AND table_name = %s);
                """,
                (table_name,)
            )

            exists = cur.fetchone()[0]

            # fix this to include column types
            print("Dummy table created. Fix!!!!")
            if not exists:
                query = sql.SQL(
                    """
                    CREATE TABLE {}
                    (
                        id
                        SERIAL
                        PRIMARY
                        KEY
                    );
                    """
                ).format(sql.Identifier(table_name))

                cur.execute(query)
                self.conn.commit()

                print(f"Table '{table_name}' created.")
            else:
                print(f"Table '{table_name}' already exists.")


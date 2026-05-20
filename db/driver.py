import os

import psycopg2
from dotenv import load_dotenv


class PostgresDriver:
    conn = None
    cur = None
    db_version = None

    def __init__(self):
        try:
            load_dotenv()
            self.conn = psycopg2.connect(
                dbname=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT"),
            )
            self.cur = self.conn.cursor()

            print('PostgreSQL database connected!')
            self.cur.execute('SELECT version()')

            self.db_version = self.cur.fetchone()
            print(f"Postgres Version: {self.db_version}")

            self.cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if self.conn is not None:
                self.conn.close()
                print('Database connection closed.')

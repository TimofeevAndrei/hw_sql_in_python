import psycopg2
from settings import PASS

with psycopg2.connect(database="ClientDB", user="postgres", password=PASS) as conn:
    def creat_tables():
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS client(
                    id SERIAL PRIMARY KEY,
                    first_name VARCHAR(40),
                    last_name VARCHAR(40),
                    email VARCHAR(40) UNIQUE
                );
                """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS phonebook(
                    id SERIAL PRIMARY KEY,
                    number INTEGER NOT NULL,
                    clientid int not null references client(id)
                );
                """)
            conn.commit()
        return
creat_tables()
conn.close()
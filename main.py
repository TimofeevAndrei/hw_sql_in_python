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

    def add_client():
        in_email = input('Введите email: ')

        with conn.cursor() as cur:
            cur.execute('select email from client')
            allmail = cur.fetchall()

            for i in allmail:
                if in_email in i:
                    print('Клиент с таким email уже существует.')
                    mailchek = 'select first_name, last_name, email from {table} where email = %s'
                    cur.execute(mailchek.format(table='client'), [in_email])
                    print(cur.fetchone())
                    return
            in_first_name = input('Введите имя: ')
            in_last_name = input('Введите фамилию: ')
            new_client = 'insert into client (first_name, last_name, email) values (%s, %s, %s)'
            cur.execute(new_client.format(table='client'), (in_first_name, in_last_name, in_email))
            conn.commit()
            print('Новый клиент успешно добавлен в базу.')
            return

    def add_phone():
        in_phone = int(input('Введите номер телефона: '))

        with conn.cursor() as cur:
            cur.execute('select number from phonebook')
            allphones = cur.fetchall()
            print(allphones)
            for i in allphones:
                if in_phone in i:
                    print('Такой номер телефона уже есть в базе.')
                    phonechek = 'select client_id from {table} where number = %s'
                    cur.execute(phonechek.format(table='phonebook'), [in_phone])
                    print(cur.fetchone())
                    return
            in_first_name = input('Введите имя: ')
            in_last_name = input('Введите фамилию: ')
            new_client = 'insert into client (first_name, last_name, email) values (%s, %s, %s)'
            cur.execute(new_client.format(table='client'), (in_first_name, in_last_name, in_email))
            conn.commit()
            print('Новый клиент успешно добавлен в базу.')
            return

add_phone()

conn.close()
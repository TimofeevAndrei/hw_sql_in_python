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
                    mailcheck = 'select first_name, last_name, email from {table} where email = %s'
                    cur.execute(mailcheck.format(table='client'), [in_email])
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
            for i in allphones:
                if in_phone in i:
                    phonechek = 'select clientid from {table} where number = %s'
                    cur.execute(phonechek.format(table='phonebook'), [in_phone])
                    phone_id=(cur.fetchone())
                    find_client = 'select first_name, last_name, email from {table} where id = %s'
                    cur.execute(find_client.format(table='client'), [phone_id])
                    result = (cur.fetchone())
                    print(f'Такой номер телефона уже принадлежит клиенту:'
                          f' {result[0]} {result[1]}, email: {result[2]}')
                    return
            matching = input('email клиента: ')
            find_client = 'select id, first_name, last_name, email from {table} where email = %s'
            cur.execute(find_client.format(table='client'), [matching])
            result = (cur.fetchone())
            new_phone = 'insert into {table} (number, clientid) values (%s, %s)'
            cur.execute(new_phone.format(table='phonebook'), (in_phone, result[0]))
            conn.commit()
            print(f'Добавилен новый номер телефона в БД и присвоен пользователю: '
                  f' {result[1]} {result[2]}, email: {result[3]}')
            return

    def edit_client():
        print('Поиск клиента осуществляеться по email, так как он уникален для каждого клиента.')
        search = input('Введите email клиента: ')
        with conn.cursor() as cur:
            find_client = 'select id, first_name, last_name, email from {table} where email = %s'
            cur.execute(find_client.format(table='client'), [search])
            result = (cur.fetchone())
            if search in result:
                print(f'Клиент найден: {result[1]} {result[2]}, email: {result[3]}')
                id_client = result[0]
                new_first_name = input('Введите новое имя:')
                new_last_name = input('Введите новую фамилию:')
                new_email = input('Введите новый email:')
                editing_client = 'update {table} set first_name=%s, last_name=%s, email=%s where id={id_client}'
                cur.execute(editing_client.format(table='client', id_client=id_client), (new_first_name, new_last_name,
                                                                                         new_email))

                check = 'select first_name, last_name, email from {table} where email = %s'
                cur.execute(check.format(table='client'), [new_email])
                result_after = (cur.fetchone())
                conn.commit()
                print(f'Пользователь: {result[1]} {result[2]}, email: {result[3]} '
                      f'отредактирован на {result_after[0]} {result_after[1]}, email: {result_after[2]}')




edit_client()

conn.close()
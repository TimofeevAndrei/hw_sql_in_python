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
                    phonecheck = 'select clientid from {table} where number = %s'
                    cur.execute(phonecheck.format(table='phonebook'), [in_phone])
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
            if result is None:
                print('Записи отсутсвуют')
            else:
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

    def delete_phone():
        request = int(input(f'По какому параметру осуществить поиск?\n'
                            f'Если по номеру телефона введите 1:\n'
                            f'Если по email то введите 2:\n'
                            f'Ввод: '))
        with conn.cursor() as cur:
            if request == 1:
                search_phone = int(input('Введите телефон клиента: '))
                phone_find = 'select number, clientid from {table} where number = %s'
                cur.execute(phone_find.format(table='phonebook'), [search_phone])
                result_phone = (cur.fetchone())
                if result_phone is None:
                    print('Записи отсутсвуют')
                else:
                    find_client_id = 'select first_name, last_name, email from {table} where id = %s'
                    cur.execute(find_client_id.format(table='client'), [result_phone[1]])
                    result_id = (cur.fetchone())
                    answer = input(f'Найдена запись {result_phone}, принадлежащая {result_id} удалить? Введите yes/no: ')
                    if answer.lower() == 'yes':
                        phone_del = 'delete from {table} where number = %s'
                        cur.execute(phone_del.format(table='phonebook'), [result_phone[0]])
                    elif answer.lower() == 'no':
                        return
                    else:
                        print('Некоректный ввод')

            elif request == 2:
                search = input('Введите email клиента: ')
                find_client_email = 'select id, first_name, last_name, email from {table} where email = %s'
                cur.execute(find_client_email.format(table='client'), [search])
                result = (cur.fetchone())
                if result is None:
                    print('Записи отсутсвуют')
                else:
                    find_phones = 'select id, number from {table} where clientid = %s'
                    cur.execute(find_phones.format(table='phonebook'), [result[0]])
                    result_phones = (cur.fetchall())
                    print(f'Клиент найден {result}')
                    sockets = []
                    for v, k in result_phones:
                        print(f'Ячейка:{v} содержит номер телефона: {k}')
                        sockets.append(v)
                    answer = int(input('Введите номер ячейки которую желаете удалить: '))
                    if answer in sockets:
                        phone_del = 'delete from {table} where id = %s'
                        cur.execute(phone_del.format(table='phonebook'), [answer])
                        print(f'ячейка №{answer} успешно удаленна.')
                    else:
                        print('Некоректный ввод')
                        return
            else:
                print('Некоректный ввод')
                return

        conn.commit()

    def delete_client():
        print('Поиск клиента осуществляеться по email, так как он уникален для каждого клиента.')
        search = input('Введите email клиента: ')
        with conn.cursor() as cur:
            find_client = 'select id, first_name, last_name, email from {table} where email = %s'
            cur.execute(find_client.format(table='client'), [search])
            result = (cur.fetchone())
            id_client = result[0]
            if search in result:
                answer = input(f'Найдена запись {result[1]} {result[2]}, email: {result[3]} удалить? Введите yes/no: ')
                if answer.lower() == 'yes':
                    phone_del = 'delete from {table} where clientid = %s'
                    cur.execute(phone_del.format(table='phonebook'), [id_client])
                    client_del = 'delete from {table} where id = %s'
                    cur.execute(client_del.format(table='client'), [id_client])
                    conn.commit()
                    print('Запись и связанные номера телефонов удалены!')
                elif answer.lower() == 'no':
                    return

    def client_search():
        print(f'Поиск по имени - 1\n'
              f'Поиск по фамилии - 2\n'
              f'Поиск по email - 3\n'
              f'Поиск по номеру телефона - 4\n')
        answ = int(input('Введите типа поиска от 1 до 4: '))
        with conn.cursor() as cur:
            if answ == 1:
                search=input('Введите имя:')
                find_client = 'select id, first_name, last_name, email from {table} where first_name = %s'
                cur.execute(find_client.format(table='client'), [search])
                result = (cur.fetchone())
                if result is None:
                    print('Записи отсутсвуют')
                else:
                    print(f'Клиент найден {result}')
            elif answ == 2:
                search=input('Введите фамилию:')
                find_client = 'select id, first_name, last_name, email from {table} where last_name = %s'
                cur.execute(find_client.format(table='client'), [search])
                result = (cur.fetchone())
                if result is None:
                    print('Записи отсутсвуют')
                else:
                    print(f'Клиент найден {result}')
            elif answ == 3:
                search=input('Введите email:')
                find_client = 'select id, first_name, last_name, email from {table} where email = %s'
                cur.execute(find_client.format(table='client'), [search])
                result = (cur.fetchone())
                if result is None:
                    print('Записи отсутсвуют')
                else:
                    print(f'Клиент найден {result}')
            elif answ == 4:
                search=input('Введите номер телефона:')
                find_client = 'select clientid from {table} where number = %s'
                cur.execute(find_client.format(table='phonebook'), [search])
                result_num = (cur.fetchone())
                find_client = 'select id, first_name, last_name, email from {table} where id = %s'
                cur.execute(find_client.format(table='client'), [result_num])
                result = (cur.fetchone())
                if result is None:
                    print('Записи отсутсвуют')
                else:
                    print(f'Клиент найден {result}')
            else:
                print('Некоректный ввод')


    print(f'Создание таблиц базы - 1\n'
          f'Добавить клиента - 2\n'
          f'Добавить телефон - 3\n'
          f'Редактировать карточку клиента - 4\n'
          f'Удалить телефон - 5\n'
          f'Удалить карточку клиента - 6\n'
          f'Поиск клиента по базе - 7\n')
    def operation():
        while True:
            user_comand = input('Введите команду:')
            if user_comand == '1':
                creat_tables()
            elif user_comand == '2':
                add_client()
            elif user_comand == '3':
                add_phone()
            elif user_comand == '4':
                edit_client()
            elif user_comand == '5':
                delete_phone()
            elif user_comand == '6':
                delete_client()
            elif user_comand == '7':
                client_search()
            else:
                print('Неверная команда')

operation()
conn.close()
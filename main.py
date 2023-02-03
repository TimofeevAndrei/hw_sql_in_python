import psycopg2
from settings import PASS


def creat_tables(cur):
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS client(
            id SERIAL PRIMARY KEY,
            first_name VARCHAR(40),
            last_name VARCHAR(40),
            email VARCHAR(40) UNIQUE
        );
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS phonebook(
            id SERIAL PRIMARY KEY,
            number INTEGER NOT NULL,
            clientid int not null references client(id)
        );
        """
    )
    conn.commit()
    return


def add_client(cur, in_email, in_first_name, in_last_name):

    cur.execute("select email from client")
    allmail = cur.fetchall()

    for i in allmail:
        if in_email in i:
            print("Клиент с таким email уже существует.")
            mailcheck = (
                "select first_name, last_name, email from {table} where email = %s"
            )
            cur.execute(mailcheck.format(table="client"), [in_email])
            print(cur.fetchone())
            return
    new_client = (
        "insert into client (first_name, last_name, email) values (%s, %s, %s)"
    )
    cur.execute(
        new_client.format(table="client"), (in_first_name, in_last_name, in_email)
    )
    conn.commit()
    print("Новый клиент успешно добавлен в базу.")
    return


def add_phone(cur, in_phone, client_id):
    phone_find = "select number, clientid from {table} where number = %s"
    cur.execute(phone_find.format(table="phonebook"), [in_phone])
    result_phone = cur.fetchone()
    if result_phone is None:
        find_client = (
            "select id, first_name, last_name, email from {table} where id = %s"
        )
        cur.execute(find_client.format(table="client"), [client_id])
        result = cur.fetchone()
        if result is None:
            print("Клиент с таким ID отсутсвуют")
        else:
            new_phone = "insert into {table} (number, clientid) values (%s, %s)"
            cur.execute(new_phone.format(table="phonebook"), (in_phone, client_id))
            conn.commit()
            print(
                f"Добавилен новый номер телефона в БД и присвоен пользователю: "
                f" {result[1]} {result[2]}, email: {result[3]}"
            )
    else:
        print(f"Номер уже в базе и принадлежит клиенту с ID {result_phone[1]}")
        return


def edit_client(cur, email, new_first_name, new_last_name, new_email):
    print(
        "Поиск клиента осуществляеться по email, так как он уникален для каждого клиента."
    )
    search = input("Введите email клиента: ")

    find_client = (
        "select id, first_name, last_name, email from {table} where email = %s"
    )
    cur.execute(find_client.format(table="client"), [search])
    result = cur.fetchone()
    if email in result:
        print(f"Клиент найден: {result[1]} {result[2]}, email: {result[3]}")
        id_client = result[0]
        editing_client = "update {table} set first_name=%s, last_name=%s, email=%s where id={id_client}"
        cur.execute(
            editing_client.format(table="client", id_client=id_client),
            (new_first_name, new_last_name, new_email),
        )

        check = "select first_name, last_name, email from {table} where email = %s"
        cur.execute(check.format(table="client"), [new_email])
        result_after = cur.fetchone()
        conn.commit()
        print(
            f"Пользователь: {result[1]} {result[2]}, email: {result[3]} "
            f"отредактирован на {result_after[0]} {result_after[1]}, email: {result_after[2]}"
        )


def delete_phone(cur, phone):

    phone_find = "select number, clientid from {table} where number = %s"
    cur.execute(phone_find.format(table="phonebook"), [phone])
    result_phone = cur.fetchone()
    if result_phone is None:
        print("Записи отсутсвуют")
    else:
        find_client_id = (
            "select first_name, last_name, email from {table} where id = %s"
        )
        cur.execute(find_client_id.format(table="client"), [result_phone[1]])
        result_id = cur.fetchone()
        print(f"Найдена запись {result_phone}, принадлежащая {result_id}, запись удалена.")
        phone_del = "delete from {table} where number = %s"
        cur.execute(phone_del.format(table="phonebook"), [result_phone[0]])
    conn.commit()


def delete_client(cur, client_id):
    find_client = (
        "select id, first_name, last_name, email from {table} where id = %s"
    )
    cur.execute(find_client.format(table="client"), [client_id])
    result = cur.fetchone()
    if result is None:
        print('Запись с таким ID не найдена')
        return
    else:
        phone_del = "delete from {table} where clientid = %s"
        cur.execute(phone_del.format(table="phonebook"), [client_id])
        client_del = "delete from {table} where id = %s"
        cur.execute(client_del.format(table="client"), [client_id])
        conn.commit()
        print(f"Запись c ID {client_id} удалена!")
        return


def client_search(cur, req):
    if type(req) == int:
        find_client = "select id, first_name, last_name, email from {table} where id = %s"
        cur.execute(find_client.format(table="client"), [req])
        result = cur.fetchone()
        if result is None:
            find_client = "select clientid from {table} where number = %s"
            cur.execute(find_client.format(table="phonebook"), [req])
            result_num = cur.fetchone()
            find_client = (
                "select id, first_name, last_name, email from {table} where id = %s"
            )
            cur.execute(find_client.format(table="client"), [result_num])
            result = cur.fetchone()
            if result is None:
                print("Записи отсутсвуют")
            else:
                print(f"Клиент найден {result}")
        else:
            print(f"Клиент найден {result}")
    else:
        find_client = "select id, first_name, last_name, email from {table} where first_name = %s"
        cur.execute(find_client.format(table="client"), [req])
        result = cur.fetchone()
        if result is None:
            find_client = "select id, first_name, last_name, email from {table} where last_name = %s"
            cur.execute(find_client.format(table="client"), [req])
            result = cur.fetchone()
            if result is None:
                find_client = (
                    "select id, first_name, last_name, email from {table} where email = %s"
                )
                cur.execute(find_client.format(table="client"), [req])
                result = cur.fetchone()
                if result is None:
                    print("Записи отсутсвуют")
                else:
                    print(f"Клиент найден {result}")
            else:
                print(f"Клиент найден {result}")
        else:
            print(f"Клиент найден {result}")








print(
    f"Создание таблиц базы - 1\n"
    f"Добавить клиента - 2\n"
    f"Добавить телефон - 3\n"
    f"Редактировать карточку клиента - 4\n"
    f"Удалить телефон - 5\n"
    f"Удалить карточку клиента - 6\n"
    f"Поиск клиента по базе - 7\n"
)


def operation():
    while True:
        user_comand = input("Введите команду:")
        if user_comand == "1":
            creat_tables(cur)
        elif user_comand == "2":
            add_client(cur, 'art@ar333t.ru', 'Bob', 'Stack')
        elif user_comand == "3":
            add_phone(cur, 58578, 10)
        elif user_comand == "4":
            edit_client(cur, 'email', 'new_first_name', 'new_last_name', 'new_email')
        elif user_comand == "5":
            delete_phone(cur, '77777')
        elif user_comand == "6":
            delete_client(cur, 6)
        elif user_comand == "7":
            client_search(cur, 5858)
        else:
            print("Неверная команда")


if __name__ == "__main__":
    with psycopg2.connect(database="ClientDB", user="postgres", password=PASS) as conn:
        with conn.cursor() as cur:
            operation()

conn.close()

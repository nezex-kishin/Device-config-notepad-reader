import psycopg2
from config import host,user,password,db_name

file = open('passqo.txt')
a = file.readlines()
i = 0
bb = 1

try:
    connection = psycopg2.connect(
        host = host,
        user = user,
        password = password,
        database = db_name
    )
    connection.autocommit = True

    def insertpasswords():
        global i, a
        while i != len(a):
            b = a[i]
            b = b[0:16]
            q = b.split()
            if len(q) < 2:
                with connection.cursor() as cursor:
                    cursor.execute(
                        f"""
                        INSERT INTO devices(kod)
                        SELECT '{q[0]}'
                        WHERE
                        NOT EXISTS (
                        SELECT kod FROM devices WHERE kod = '{q[0]}'
                        );
                        """
                    )
                break
            else:
                if i + 2 > len(a):
                    with connection.cursor() as cursor:
                        cursor.execute(
                            f"""INSERT INTO devices (kod,masterpassword) 
                                    SELECT '{q[0]}','{q[1]}'
                                        WHERE
                                        NOT EXISTS (
                                        SELECT 1 FROM devices WHERE kod = '{q[0]}'
                                        );
                                        """
                        )
                    break
                else:
                    c = a[i + 1]
                    if b[0:7] == c[0:7]:
                        with connection.cursor() as cursor:
                            cursor.execute(
                                f"""
                                INSERT INTO shadowdevices (kod,masterpassword)
                                    SELECT '{q[0]}','{q[1]}'
                                    WHERE
                                    NOT EXISTS (
                                    SELECT 1 FROM shadowdevices WHERE masterpassword = '{q[1]}' AND kod = '{q[0]}'
                                    );
                                """
                            )
                        i += 1
                        continue
                    else:
                        with connection.cursor() as cursor:
                            cursor.execute(
                                f"""INSERT INTO devices (kod,masterpassword) 
                                        SELECT '{q[0]}','{q[1]}'
                                        WHERE
                                        NOT EXISTS (
                                        SELECT 1 FROM devices WHERE kod = '{q[0]}'
                                        );    
                                        """
                            )
                        i += 1
                        continue
    def updatepasswords():
        global i, a
        while i != len(a):
            b = a[i]
            b = b[0:16]
            q = b.split()
            if len(q) < 2:
                i += 1
                continue
            else:
                if i + 2 > len(a):
                    with connection.cursor() as cursor:
                        cursor.execute(
                            f"""
                            INSERT INTO shadowdevices
                                SELECT '{q[0]}',masterpassword  FROM devices
                                WHERE NOT EXISTS(
                                SELECT kod,masterpassword FROM shadowdevices WHERE kod = '{q[0]}' AND masterpassword = masterpassword );
                             """)
                    with connection.cursor() as cursor:
                        cursor.execute(
                             f"""
                                UPDATE devices
                                    SET masterpassword = '{q[1]}'
                                    WHERE (masterpassword IS NULL OR masterpassword <> '{q[1]}')  AND kod = '{q[0]}';
                            """
                        )
                    break
                else:
                    c = a[i + 1]
                    if b[0:7] == c[0:7]:
                        with connection.cursor() as cursor:
                            cursor.execute(
                        f"""
                        INSERT INTO shadowdevices (kod,masterpassword)
                            SELECT '{q[0]}','{q[1]}'
                            WHERE
                            NOT EXISTS (
                            SELECT 1 FROM shadowdevices WHERE masterpassword = '{q[1]}' AND kod = '{q[0]}')
                            ;
                        """)
                        i += 1
                        continue
                    else:
                        with connection.cursor() as cursor:
                            cursor.execute(
                            f"""
                                UPDATE devices
                                SET masterpassword = '{q[1]}'
                                WHERE (masterpassword IS NULL OR masterpassword <> '{q[1]}')  AND kod = '{q[0]}';
                            """
                            )
                        i += 1
                        continue
    def droptable():
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                DROP TABLE devices,shadowdevices;
                """
            )
    def createtables():
        with connection.cursor() as cursor:
            cursor.execute(
                """CREATE TABLE devices(
                id serial PRIMARY KEY,
                kod varchar(50),
                masterpassword varchar(50)           
                );
                """
            )
        with connection.cursor() as cursor:
            cursor.execute(
                """CREATE TABLE shadowdevices(
                id serial PRIMARY KEY,
                kod varchar(50),
                masterpassword varchar(50)
                );
                """
            )

    while bb != 0:
        bb = int(input('\n Введите номер операции \n 1:Вставить пароли из блокнота \n 2:Обновить пароли в таблице \n 3:Удалить таблицу \n 4:Создать новую таблицу \n\n Введите 0 чтобы закончить программу \n Ввод: '))
        if bb == 1:
            insertpasswords()
        elif bb == 2:
            updatepasswords()
        elif bb == 3:
            droptable()
        elif bb == 4:
            createtables()
        elif bb > 4 or bb < 0:
            print('Неправильно введён номер операции, повторите снова!')

except Exception as _ex:
    print("[INFO] Error while working with PostgreSQL", _ex)
import sqlite3

class db:
    def __init__(self, db):
        self.connection = sqlite3.connect(db, check_same_thread=False)
        self.cursor = self.connection.cursor()
        self.cursor.execute(
            'CREATE TABLE IF NOT EXISTS Logs ( id INTEGER PRIMARY KEY AUTOINCREMENT, log TEXT NOT NULL, date TEXT NOT NULL, user TEXT NOT NULL);')
        self.cursor.execute(
            'CREATE TABLE IF NOT EXISTS Users ( id INTEGER PRIMARY KEY AUTOINCREMENT, login TEXT NOT NULL, password TEXT NOT NULL, permissions TEXT NOT NULL, codeword VARCHAR(6) NOT NULL);')
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS employees ( id INTEGER PRIMARY KEY AUTOINCREMENT, last_name TEXT NOT NULL, first_name TEXT NOT NULL, middle_name TEXT, phone VARCHAR(20) NOT NULL, 
            email TEXT NOT NULL, positionId INTEGER NOT NULL, experience INTEGER NOT NULL, workplaceId INTEGER NOT NULL, dateOfFiring TEXT NULL, dateOfHiring TEXT NULL, status TEXT DEFAULT 'Принят на работу', FOREIGN KEY (positionId) REFERENCES positions(id), FOREIGN KEY (workplaceId) REFERENCES workplaces(id));""")
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS interns ( id INTEGER PRIMARY KEY AUTOINCREMENT, last_name TEXT NOT NULL, first_name TEXT NOT NULL, middle_name TEXT, phone VARCHAR(20) NOT NULL, 
            email TEXT NOT NULL, positionId INTEGER NOT NULL, experience INTEGER NOT NULL, workplaceId INTEGER NOT NULL, dateOfFiring TEXT NULL, dateOfHiring TEXT NULL, status TEXT DEFAULT 'Стажируется', FOREIGN KEY (positionId) REFERENCES positions(id), FOREIGN KEY (workplaceId) REFERENCES workplaces(id));""")
        self.cursor.execute(
            'CREATE TABLE IF NOT EXISTS workplaces ( id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, address TEXT NOT NULL);')
        self.cursor.execute(
            'CREATE TABLE IF NOT EXISTS positions ( id INTEGER PRIMARY KEY AUTOINCREMENT, profession TEXT NOT NULL, salary INTEGER NOT NULL);')
        self.connection.commit()

    def selectUser(self, login):
        cursor = self.connection.execute('SELECT * FROM Users WHERE (login=?)', (str(login),))
        user = cursor.fetchone()
        return user

    def selectLogs(self):
        cursor = self.connection.execute('SELECT * FROM Logs')
        return cursor.fetchall()

    def selectEmployees(self):
        cursor = self.connection.execute('SELECT * FROM Employees')
        return cursor.fetchall()

    def selectInterns(self):
        cursor = self.connection.execute('SELECT * FROM interns')
        return cursor.fetchall()

    def selectPositionById(self, id):
        cursor = self.connection.execute('SELECT profession FROM positions WHERE (id=?)', (str(id),))
        return cursor.fetchone()

    def selectWorkplaceById(self, id):
        cursor = self.connection.execute('SELECT name FROM workplaces WHERE (id=?)', (str(id),))
        return cursor.fetchone()

    def selectPositions(self):
        cursor = self.connection.execute('SELECT profession FROM positions')
        return cursor.fetchall()

    def selectWorkplaces(self):
        cursor = self.connection.execute('SELECT name FROM workplaces')
        return cursor.fetchall()

    def getIdByProfession(self, name):
        cursor = self.connection.execute('SELECT id FROM positions WHERE profession LIKE "%' + name + '%"')
        return cursor.fetchone()

    def getIdByWorkplace(self, name):
        cursor = self.connection.execute('SELECT id FROM workplaces WHERE name LIKE "%' + name + '%"')
        return cursor.fetchone()

    def getSalaryByProfession(self, name):
        cursor = self.connection.execute('SELECT salary FROM positions WHERE profession LIKE "%' + name + '%"')
        return cursor.fetchone()[0]

    def selectEmployeesBy(self, msg):
        if msg == "" or msg == "Поиск...":
            cursor = self.connection.execute('SELECT * FROM Employees WHERE status != "Увольнение"')
            return cursor.fetchall()

        cursor = self.connection.execute(
            '''SELECT * FROM Employees WHERE id LIKE "%''' + msg + '''%" OR last_name LIKE "%''' + msg + '''%" 
                                                OR first_name LIKE "%''' + msg + '''%" OR middle_name LIKE "%''' + msg + '''%" OR phone LIKE "%''' + msg + '''%"
                                                OR email LIKE "%''' + msg + '''%" OR positionId LIKE "%''' + msg + '''%" OR workplaceId LIKE "%''' + msg + '%" AND status != "Увольнение"''')
        result = cursor.fetchall()
        try:
            try:
                msg = msg.capitalize()
            except:
                pass
            s = self.getIdByProfession(msg)
            if s is not None:
                cursor = self.connection.execute('SELECT * FROM employees WHERE positionId LIKE "' + str(s[0]) + '"')
                r = cursor.fetchall()
                if r != [] and r is not None:
                    for i in r:
                        result.append(i)
            o = self.getIdByWorkplace(msg)
            if o is not None:
                cursor = self.connection.execute('SELECT * FROM employees WHERE workplaceId LIKE "' + str(o[0]) + '"')
                r = cursor.fetchall()
                if r != [] and r is not None:
                    for i in r:
                        result.append(i)
        except Exception as e:
            print(e)

        for i in result:
            if i[11] == "Увольнение":
                result.remove(i)

        return result

    def selectInternsBy(self, msg):
        if msg == "" or msg == "Поиск...":
            cursor = self.connection.execute('SELECT * FROM interns WHERE status != "Увольнение"')
            return cursor.fetchall()

        cursor = self.connection.execute(
            '''SELECT * FROM interns WHERE id LIKE "%''' + msg + '''%" OR last_name LIKE "%''' + msg + '''%" 
                                                OR first_name LIKE "%''' + msg + '''%" OR middle_name LIKE "%''' + msg + '''%" OR phone LIKE "%''' + msg + '''%"
                                                OR email LIKE "%''' + msg + '''%" OR positionId LIKE "%''' + msg + '''%" OR workplaceId LIKE "%''' + msg + '''%"''')
        result = cursor.fetchall()
        try:
            try:
                msg = msg.capitalize()
            except:
                pass
            s = self.getIdByProfession(msg)
            if s is not None:
                cursor = self.connection.execute('SELECT * FROM interns WHERE positionId LIKE "' + str(s[0]) + '"')
                r = cursor.fetchall()
                if r != [] and r is not None:
                    for i in r:
                        result.append(i)
            o = self.getIdByWorkplace(msg)
            if o is not None:
                cursor = self.connection.execute('SELECT * FROM interns WHERE workplaceId LIKE "' + str(o[0]) + '"')
                r = cursor.fetchall()
                if r != [] and r is not None:
                    for i in r:
                        result.append(i)
        except Exception as e:
            print(e)

        for i in result:
            if i[11] == "Увольнение":
                result.remove(i)

        return result

    def selectLogsBy(self, msg):
        if msg == "" or msg == "Поиск...":
            cursor = self.connection.execute('SELECT * FROM Logs')
            return cursor.fetchall()

        cursor = self.connection.execute(
            '''SELECT * FROM Logs WHERE id LIKE "%''' + msg + '''%" OR log LIKE "%''' + msg + '''%" 
                                                OR date LIKE "%''' + msg + '''%" OR user LIKE "%''' + msg + '''%"''')
        result = cursor.fetchall()
        return result

    def deleteEmployee(self, last_name, phone, email, date=None):
        cursor = self.connection.execute("UPDATE Employees SET dateOfFiring=?, status='Увольнение' WHERE last_name=? AND phone=? AND email=?", (date, last_name, phone, email))
        self.connection.commit()

    def deleteIntern(self, last_name, phone, email, date=None):
        cursor = self.connection.execute("UPDATE interns SET dateOfFiring=?, status='Увольнение' WHERE last_name=? AND phone=? AND email=?", (date, last_name, phone, email))
        self.connection.commit()

    def updateTable(self, l, p, e, table, last_name, first_name, middle_name, phone, email, posId, experience, offId):
        if table == 0:
            cursor = self.connection.execute(
                "UPDATE employees SET last_name=?, first_name=?, middle_name=?, phone=?, email=?, positionId=?, "
                "experience=?, workplaceId=? WHERE (last_name=? AND phone=? AND email=?)",
                (last_name, first_name, middle_name, phone, email, posId, experience, offId, l, p, e))
        else:
            cursor = self.connection.execute(
                "UPDATE interns SET last_name=?, first_name=?, middle_name=?, phone=?, email=?, positionId=?, "
                "experience=?, workplaceId=? WHERE (last_name=? AND phone=? AND email=?)",
                (last_name, first_name, middle_name, phone, email, posId, experience, offId, l, p, e))
        self.connection.commit()
        return True

    def acceptIntern(self, last_name, phone, email, dateOfHiring):
        cursor = self.connection.execute("""INSERT INTO Employees (last_name, first_name, middle_name, phone, 
                                            email, positionId, experience, workplaceId) SELECT last_name, first_name, middle_name, phone, 
                                            email, positionId, experience, workplaceId FROM interns WHERE (last_name=? AND phone=? AND email=?)""", (last_name, phone, email))
        cursor = self.connection.execute("UPDATE Employees SET dateOfHiring=?, status='Принят на работу' WHERE last_name=? AND phone=? AND email=?", (dateOfHiring, last_name, phone, email))
        cursor = self.connection.execute("DELETE FROM interns WHERE (last_name=? AND phone=? AND email=?)", (last_name, phone, email))
        self.connection.commit()

    def insertEmployee(self, last_name, first_name, middle_name, phone, email, posId, experience, offId, dateOfHiring):
        cursor = self.connection.execute(
            'SELECT * FROM Employees WHERE (last_name=? AND first_name=? AND middle_name=? AND phone=? AND email=? AND positionId=? AND experience=? AND workplaceId=?)',
            (last_name, first_name, middle_name, phone, email, posId, experience, offId))
        entry = cursor.fetchone()
        if entry is None:
            self.cursor.execute(
                'INSERT INTO Employees (last_name, first_name, middle_name, phone, email, positionId, experience, workplaceId, dateOfHiring) VALUES (?,?,?,?,?,?,?,?,?)',
                (last_name, first_name, middle_name, phone, email, posId, experience, offId, dateOfHiring))
            self.connection.commit()
            return True
        else:
            return False

    def insertIntern(self, last_name, first_name, middle_name, phone, email, posId, experience, offId, dateOfHiring):
        cursor = self.connection.execute(
            'SELECT * FROM interns WHERE (last_name=? AND first_name=? AND middle_name=? AND phone=? AND email=? AND positionId=? AND experience=? AND workplaceId=?)',
            (last_name, first_name, middle_name, phone, email, posId, experience, offId))
        entry = cursor.fetchone()
        if entry is None:
            self.cursor.execute(
                'INSERT INTO interns (last_name, first_name, middle_name, phone, email, positionId, experience, workplaceId, dateOfHiring) VALUES (?,?,?,?,?,?,?,?,?)',
                (last_name, first_name, middle_name, phone, email, posId, experience, offId, dateOfHiring))
            self.connection.commit()
            return True
        else:
            return False

    def insertUser(self, login, password, codeword):
        cursor = self.connection.execute('INSERT INTO Users (login, password, permissions, codeword) VALUES (?,?,?,?)', (login, password, "user", codeword))
        self.connection.commit()
        return True

    def insertLog(self, log, date, user):
        try:
            cursor = self.connection.execute('INSERT INTO Logs (log, date, user) VALUES (?,?,?)',
                                             (log, date, user))
            self.connection.commit()
        except:
            pass
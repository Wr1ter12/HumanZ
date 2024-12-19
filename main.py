import sys
from datetime import date, datetime
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QWidget, QPushButton, QApplication, QTableWidgetItem, QComboBox, QMessageBox,
    QTabWidget, QTableWidget, QGridLayout, QLabel, QFormLayout, QLineEdit, QAbstractItemView,
    QGraphicsDropShadowEffect, QMenu)

from re import match
from sql import db
from document import docWriter
from excel import Excel

db = db("HumanZDatabase.db")
doc = docWriter()
exc = Excel()

current_user = "guest"


class Window(QWidget):

    def __init__(self):
        super().__init__()
        self.layout = QGridLayout()
        self.layout.setSpacing(15)
        self.setWindowTitle("HumanZ")
        self.setWindowIcon(QIcon('HumanZIcon.png'))
        self.setFixedSize(250, 180)
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.setLayout(self.layout)
        self.setStyleSheet(open("style.qss", "r").read())


class LoginWindow(Window):

    def __init__(self):
        super().__init__()
        self.setFixedSize(250, 210)

        title = QLabel("Отдел Кадров системы HumanZ")
        title.setProperty("class", "heading")
        self.layout.addWidget(title, 0, 0, 1, 3, Qt.AlignmentFlag.AlignCenter)

        login = QLabel("Логин:")
        self.layout.addWidget(login, 1, 0)
        self.loginInput = QLineEdit()
        self.layout.addWidget(self.loginInput, 1, 1, 1, 2)

        password = QLabel("Пароль:")
        self.layout.addWidget(password, 2, 0)
        self.passwordInput = QLineEdit()
        self.passwordInput.setEchoMode(QLineEdit.EchoMode.Password)
        self.layout.addWidget(self.passwordInput, 2, 1, 1, 2)

        buttonRecover = QPushButton("Восстановить пароль")
        buttonRecover.clicked.connect(self.recoverPassword)
        self.layout.addWidget(buttonRecover, 3, 0, 1, 3)

        button = QPushButton("Войти")
        button.clicked.connect(self.login)
        self.layout.addWidget(button, 4, 0, 1, 3)

        self.show()

        for w in self.findChildren(QWidget):
            shadow = QGraphicsDropShadowEffect(blurRadius=30, xOffset=0, yOffset=0)
            w.setGraphicsEffect(shadow)

    def recoverPassword(self):
        global recoveryWindow
        recoveryWindow = None
        recoveryWindow = RecoveryWindow()

    def login(self):
        global current_user

        login = db.selectUser(self.loginInput.text())
        if login:
            if self.passwordInput.text() == login[2]:
                self.mainWindow = MainWindow(login[3])
                self.mainWindow.show()
                current_user = login[1]
                self.close()
            else:
                QMessageBox.critical(self, 'Ошибка', 'Некорректный пароль!')
        else:
            QMessageBox.critical(self, 'Ошибка', 'Некорректный логин!')


class RecoveryWindow(Window):

    def __init__(self):
        super().__init__()
        self.setFixedSize(250, 180)

        title = QLabel("Отдел Кадров системы HumanZ")
        title.setProperty("class", "heading")
        self.layout.addWidget(title, 0, 0, 1, 3, Qt.AlignmentFlag.AlignCenter)

        login = QLabel("Логин:")
        self.layout.addWidget(login, 1, 0)
        self.loginInput = QLineEdit()
        self.layout.addWidget(self.loginInput, 1, 1, 1, 2)

        codeword = QLabel("Кодовое слово:")
        self.layout.addWidget(codeword, 2, 0)
        self.codewordInput = QLineEdit()
        self.layout.addWidget(self.codewordInput, 2, 1, 1, 2)

        button = QPushButton("Восстановить пароль")
        button.clicked.connect(self.recoverPassword)
        self.layout.addWidget(button, 4, 0, 1, 3)

        self.show()

        for w in self.findChildren(QWidget):
            shadow = QGraphicsDropShadowEffect(blurRadius=30, xOffset=0, yOffset=0)
            w.setGraphicsEffect(shadow)

    def recoverPassword(self):
        login = db.selectUser(self.loginInput.text())
        if login:
            if self.codewordInput.text() == login[4]:
                QMessageBox.information(self, 'Успешно', f'Ваш пароль: {login[2]}')
            else:
                QMessageBox.critical(self, 'Ошибка', 'Некорректное кодовое слово!')
        else:
            QMessageBox.critical(self, 'Ошибка', 'Некорректный логин!')


class EditWindow(Window):

    def __init__(self, tab, row, table):
        super().__init__()
        self.setFixedSize(700, 340)

        self.l = row[0]
        self.p = row[3]
        self.e = row[4]
        self.table = table
        self.tab = tab

        formAdd = QWidget(self)
        FormLayout = QFormLayout(formAdd)
        formAdd.setLayout(FormLayout)

        self.last_name = QLineEdit(formAdd)
        self.last_name.setText(row[0])
        self.first_name = QLineEdit(formAdd)
        self.first_name.setText(row[1])
        self.middle_name = QLineEdit(formAdd)
        self.middle_name.setText(row[2])
        self.phone = QLineEdit(formAdd)
        self.phone.setText(row[3])
        self.email = QLineEdit(formAdd)
        self.email.setText(row[4])
        self.position = QComboBox(formAdd)
        p = db.selectPositions()
        self.position.addItems(i[0] for i in p)
        index = self.position.findText(row[5])
        self.position.setCurrentIndex(index)
        self.experience = QLineEdit(formAdd)
        self.experience.setText(row[6])
        self.workplace = QComboBox(formAdd)
        o = db.selectWorkplaces()
        self.workplace.addItems(i[0] for i in o)
        index = self.workplace.findText(row[7])
        self.workplace.setCurrentIndex(index)

        FormLayout.addRow('Фамилия:', self.last_name)
        FormLayout.addRow('Имя:', self.first_name)
        FormLayout.addRow('Отчество:', self.middle_name)
        FormLayout.addRow('Телефон:', self.phone)
        FormLayout.addRow('Почта:', self.email)
        FormLayout.addRow('Должность', self.position)
        FormLayout.addRow('Опыт:', self.experience)
        FormLayout.addRow('Адрес работы:', self.workplace)

        buttonChange = QPushButton('Изменить')
        buttonChange.clicked.connect(self.editRow)
        FormLayout.addRow(buttonChange)

        self.layout.addWidget(formAdd)

        self.show()

        for w in self.findChildren(QWidget):
            shadow = QGraphicsDropShadowEffect(blurRadius=30, xOffset=0, yOffset=0)
            w.setGraphicsEffect(shadow)

    def editRow(self):
        button = QMessageBox.question(
            self,
            'Подтверждение',
            'Вы уверены, что хотите изменить выделенную строку?',
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No
        )

        if button == QMessageBox.StandardButton.Yes:
            if not self.valid():
                return

            position = self.position.currentIndex() + 1
            workplace = self.workplace.currentIndex() + 1

            db.updateTable(self.l, self.p, self.e, self.table, self.last_name.text().strip(),
                           self.first_name.text().strip(),
                           self.middle_name.text().strip(),
                           self.phone.text().strip(), self.email.text().strip(), position,
                           self.experience.text().strip(), workplace)
            db.insertLog("Изменение строки " + self.l,
                         str(datetime.now().time().strftime("%H:%M:%S")) + " | " + str(
                             date.today().strftime('%d.%m.%Y')), current_user)
        try:
            if self.table == 0:
                self.tab.getEmployees("")
            else:
                self.tab.getInterns("")
        except:
            pass

    def valid(self):
        first_name = self.first_name.text().strip()
        last_name = self.last_name.text().strip()
        phone = self.phone.text().strip()
        email = self.email.text().strip()

        if not first_name:
            QMessageBox.critical(self, 'Ошибка', 'Введите имя!')
            self.first_name.setFocus()
            return False

        if not last_name:
            QMessageBox.critical(self, 'Ошибка', 'Введите фамилию!')
            self.last_name.setFocus()
            return False

        if not phone:
            QMessageBox.critical(self, 'Ошибка', 'Введите номер телефона!')
            self.phone.setFocus()
            return False

        if not match(r'^\+?[1-9]\d{1,14}$', phone) or not len(phone) >= 7 or not len(phone) <= 15:
            QMessageBox.critical(self, 'Ошибка', 'Некорректный формат номера телефона!')
            self.phone.setFocus()
            return False

        if not phone.startswith("8") and not phone.startswith("7") and not phone.startswith("+7"):
            QMessageBox.critical(self, 'Ошибка', 'Некорректный формат номера телефона!')
            self.phone.setFocus()
            return False

        if not match(r"^[\w\.\+\-]+\@[\w]+\.[a-z]{2,3}$", email):
            QMessageBox.critical(self, 'Ошибка', 'Некорректный формат почты!')
            self.email.setFocus()
            return False

        try:
            experience = int(self.experience.text().strip())
        except ValueError:
            QMessageBox.critical(self, 'Ошибка', 'Недопустимое значение опыта!')
            self.experience.setFocus()
            return False

        if experience < 0 or experience > 150:
            QMessageBox.critical(self, 'Ошибка', 'Недопустимое значение опыта!')
            self.experience.setFocus()
            return False

        return True

    def resetForm(self):
        self.first_name.clear()
        self.last_name.clear()
        self.middle_name.clear()
        self.phone.clear()
        self.email.clear()
        self.experience.clear()


class MainWindow(Window):

    def __init__(self, permission):
        super().__init__()
        self.setFixedSize(800, 525)

        self.tabWidget = TabWidget(self, permission)
        self.layout.addWidget(self.tabWidget, 0, 0, Qt.AlignmentFlag.AlignCenter)

        for w in self.findChildren(QWidget):
            shadow = QGraphicsDropShadowEffect(blurRadius=25, xOffset=0, yOffset=0)
            w.setGraphicsEffect(shadow)

    def toLogWindow(self):
        global logWindow
        logWindow = None
        logWindow = LogWindow()

    def quit(self):
        global loginWindow
        loginWindow = None
        loginWindow = LoginWindow()


class LogWindow(Window):

    def __init__(self):
        super().__init__()
        self.setFixedSize(500, 250)

        self.inputSearch = QLineEdit()
        self.inputSearch.setPlaceholderText("Найти...")
        self.layout.addWidget(self.inputSearch, 0, 0, 1, 2, Qt.AlignmentFlag.AlignTop)
        self.inputSearch.setFixedSize(370, 35)

        buttonSearch = QPushButton("Поиск")
        buttonSearch.clicked.connect(lambda: self.getLogs(self.inputSearch.text()))
        buttonSearch.setFixedSize(90, 35)
        self.layout.addWidget(buttonSearch, 0, 1, Qt.AlignmentFlag.AlignTop)

        logs = db.selectLogs()

        self.tableLogs = QTableWidget(self)
        self.tableLogs.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tableLogs.setFixedSize(480, 175)
        self.layout.addWidget(self.tableLogs, 1, 0, Qt.AlignmentFlag.AlignTop)

        self.tableLogs.setColumnCount(3)
        self.tableLogs.setColumnWidth(0, 240)
        self.tableLogs.setColumnWidth(1, 123)
        self.tableLogs.setColumnWidth(2, 100)

        self.tableLogs.setHorizontalHeaderLabels(
            ("Событие", "Дата", "Пользователь"))

        self.tableLogs.hide()

        self.lblLogs = QLabel("События отсутствуют")
        self.lblLogs.setProperty("class", "heading")
        self.layout.addWidget(self.lblLogs, 0, 0, 1, 2, Qt.AlignmentFlag.AlignCenter)

        if logs is not None and logs != []:
            self.tableLogs.show()
            self.lblLogs.hide()

            self.getLogsTable(logs)
        else:
            self.lblLogs.show()

        self.show()

        for w in self.findChildren(QWidget):
            shadow = QGraphicsDropShadowEffect(blurRadius=30, xOffset=0, yOffset=0)
            w.setGraphicsEffect(shadow)

    def getLogsTable(self, logs):
        self.tableLogs.setRowCount(len(logs))

        row = 0
        for l in logs:
            self.tableLogs.setItem(row, 0, QTableWidgetItem(l[1]))
            self.tableLogs.setItem(row, 1, QTableWidgetItem(l[2]))
            self.tableLogs.setItem(row, 2, QTableWidgetItem(l[3]))
            row += 1

    def getLogs(self, msg):
        log = db.selectLogsBy(msg)
        l = len(log)
        if l > 0:
            self.clearTable(self.tableLogs)
            self.tableLogs.setRowCount(l)

            row = 0
            for l in log:
                self.tableLogs.setItem(row, 0, QTableWidgetItem(l[1]))
                self.tableLogs.setItem(row, 1, QTableWidgetItem(l[2]))
                self.tableLogs.setItem(row, 2, QTableWidgetItem(l[3]))
                row += 1
            return 0
        QMessageBox.critical(self, 'Ошибка', 'Нет таких событий!')

    def clearTable(self, table):
        while table.rowCount() > 0:
            table.removeRow(0)

class TabWidget(QWidget):

    def __init__(self, parent, permission):
        super(QWidget, self).__init__(parent)
        self.layoutTab = QGridLayout(self)
        self.setLayout(self.layoutTab)
        self.setFixedSize(700, 425)

        self.tableEmployees = None
        self.tableInterns = None

        self.perm = permission

        self.tab = QTabWidget(self)

        EmpPage = QWidget(self)
        self.layoutEmp = QGridLayout()
        EmpPage.setLayout(self.layoutEmp)

        self.inputSearch1 = QLineEdit()
        self.inputSearch1.setPlaceholderText("Найти...")
        self.layoutEmp.addWidget(self.inputSearch1, 0, 0, 1, 2, Qt.AlignmentFlag.AlignTop)
        self.inputSearch1.setFixedSize(560, 35)

        buttonSearch = QPushButton("Поиск")
        buttonSearch.clicked.connect(lambda: self.getEmployees(self.inputSearch1.text()))
        buttonSearch.setFixedSize(90, 35)
        self.layoutEmp.addWidget(buttonSearch, 0, 1, Qt.AlignmentFlag.AlignTop)

        self.contextMenu = QMenu(self)
        act1 = self.contextMenu.addAction("Переместить в сотрудники")
        act1.triggered.connect(self.acceptRow)
        act2 = self.contextMenu.addAction("Изменить данные")
        act2.triggered.connect(self.toEditWindow)

        if self.perm == "admin":
            act3 = self.contextMenu.addAction("Удалить")
            act3.triggered.connect(self.deleteRow)

        employees = db.selectEmployeesBy("")

        self.tableEmployees = QTableWidget(self)
        self.tableEmployees.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tableEmployees.setFixedSize(664, 269)
        self.layoutEmp.addWidget(self.tableEmployees, 1, 0, Qt.AlignmentFlag.AlignTop)

        self.tableEmployees.setColumnCount(8)

        self.tableEmployees.setHorizontalHeaderLabels(
            ("Фамилия", "Имя", "Отчество", "Телефон", "Почта", "Должность", "Опыт", "Адрес"))

        self.tableEmployees.hide()

        self.lblEmp = QLabel("Сотрудники отсутствуют")
        self.lblEmp.setProperty("class", "heading")
        self.layoutEmp.addWidget(self.lblEmp, 0, 0, 1, 2, Qt.AlignmentFlag.AlignCenter)

        if employees is not None and employees != []:
            self.tableEmployees.show()
            self.lblEmp.hide()

            self.getEmpTable(employees)
        else:
            self.lblEmp.show()

        InternsPage = QWidget(self)
        self.layoutInt = QGridLayout()
        InternsPage.setLayout(self.layoutInt)

        self.inputSearch2 = QLineEdit()
        self.inputSearch2.setPlaceholderText("Найти...")
        self.layoutInt.addWidget(self.inputSearch2, 0, 0, 1, 2, Qt.AlignmentFlag.AlignTop)
        self.inputSearch2.setFixedSize(560, 35)

        buttonSearch = QPushButton("Поиск")
        buttonSearch.clicked.connect(lambda: self.getInterns(self.inputSearch2.text()))
        buttonSearch.setFixedSize(90, 35)
        self.layoutInt.addWidget(buttonSearch, 0, 1, Qt.AlignmentFlag.AlignTop)

        interns = db.selectInternsBy("")

        self.tableInterns = QTableWidget(self)
        self.tableInterns.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tableInterns.setFixedSize(664, 269)
        self.layoutInt.addWidget(self.tableInterns, 1, 0, Qt.AlignmentFlag.AlignTop)

        self.tableInterns.setColumnCount(8)

        self.tableInterns.setHorizontalHeaderLabels(
            ("Фамилия", "Имя", "Отчество", "Телефон", "Почта", "Должность", "Опыт", "Адрес"))

        self.tableInterns.hide()

        self.lblInterns = QLabel("Стажеры отсутствуют")
        self.lblInterns.setProperty("class", "heading")
        self.layoutInt.addWidget(self.lblInterns, 0, 0, 1, 2, Qt.AlignmentFlag.AlignCenter)

        if interns is not None and interns != []:
            self.tableInterns.show()
            self.lblInterns.hide()

            self.getIntTable(interns)

        else:
            self.lblInterns.show()

        if self.perm == "admin":
            formAdd = QWidget(self)
            FormLayout = QFormLayout(formAdd)
            formAdd.setLayout(FormLayout)

            self.tableBox = QComboBox(formAdd)
            self.tableBox.addItems(['Сотрудники', 'Стажеры'])
            self.first_name = QLineEdit(formAdd)
            self.last_name = QLineEdit(formAdd)
            self.middle_name = QLineEdit(formAdd)
            self.phone = QLineEdit(formAdd)
            self.email = QLineEdit(formAdd)
            self.position = QComboBox(formAdd)
            p = db.selectPositions()
            self.position.addItems(i[0] for i in p)
            self.experience = QLineEdit(formAdd)
            self.workplace = QComboBox(formAdd)
            o = db.selectWorkplaces()
            self.workplace.addItems(i[0] for i in o)

            FormLayout.addRow('Таблица:', self.tableBox)
            FormLayout.addRow('Фамилия:', self.last_name)
            FormLayout.addRow('Имя:', self.first_name)
            FormLayout.addRow('Отчество:', self.middle_name)
            FormLayout.addRow('Телефон:', self.phone)
            FormLayout.addRow('Почта:', self.email)
            FormLayout.addRow('Должность', self.position)
            FormLayout.addRow('Опыт:', self.experience)
            FormLayout.addRow('Адрес работы:', self.workplace)

            buttonAdd = QPushButton('Добавить')
            buttonAdd.clicked.connect(self.addRow)
            FormLayout.addRow(buttonAdd)

            # <------ Форма №2 ------->
            formAdd2 = QWidget(self)
            FormLayout2 = QFormLayout(formAdd2)
            formAdd2.setLayout(FormLayout)

            self.loginForm = QLineEdit(formAdd2)
            self.passwordForm = QLineEdit(formAdd2)
            self.codewordForm = QLineEdit(formAdd2)

            FormLayout2.addRow('Логин:', self.loginForm)
            FormLayout2.addRow('Пароль:', self.passwordForm)
            FormLayout2.addRow('Кодовое слово:', self.codewordForm)

            self.buttonAddUser = QPushButton('Добавить')
            self.buttonAddUser.clicked.connect(self.addUser)
            FormLayout2.addRow(self.buttonAddUser)

        self.tab.addTab(EmpPage, 'Сотрудники')
        self.tab.addTab(InternsPage, 'Стажеры')
        if permission == "admin":
            self.tab.addTab(formAdd, 'Добавить')
            self.tab.addTab(formAdd2, 'Пользователи')

        self.layoutTab.addWidget(self.tab, 0, 0, 2, 1)

        buttonQuit = QPushButton("Выйти из системы")
        buttonQuit.clicked.connect(MainWindow.quit)
        self.layoutTab.addWidget(buttonQuit, 2, 0,
                                 alignment=Qt.AlignmentFlag.AlignLeft)

        buttonExport = QPushButton("Экспортировать")
        buttonExport.clicked.connect(self.export)
        self.layoutTab.addWidget(buttonExport, 2, 0,
                                 alignment=Qt.AlignmentFlag.AlignCenter)

        if permission == "admin":
            buttonQuit = QPushButton("Журнал событий")
            buttonQuit.clicked.connect(MainWindow.toLogWindow)
            self.layoutTab.addWidget(buttonQuit, 2, 0,
                                     alignment=Qt.AlignmentFlag.AlignRight)

        for w in self.findChildren(QWidget):
            shadow = QGraphicsDropShadowEffect(blurRadius=25, xOffset=0, yOffset=0)
            w.setGraphicsEffect(shadow)

    def contextMenuEvent(self, event):
        self.contextMenu.exec(event.globalPos())

    def export(self):
        button = QMessageBox.question(
            self,
            'Подтверждение',
            'Вы уверены, что хотите экспортировать данную таблицу?',
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No
        )

        if button == QMessageBox.StandardButton.Yes:
            if self.tab.currentIndex() == 0:
                table = "employees"
                file = "Сотрудники.xlsx"
            elif self.tab.currentIndex() == 1:
                table = "interns"
                file = "Стажеры.xlsx"
            else:
                return
            exc.fromSQLtoExcel(table, file, db.connection)
            QMessageBox.information(self, 'Успешно', 'Таблица была успешно экспортирована!')

    def deleteRow(self):
        global current_user

        if self.tab.currentIndex() == 0:
            table = self.tableEmployees
            txt = self.lblEmp
        elif self.tab.currentIndex() == 1:
            table = self.tableInterns
            txt = self.lblInterns
        else:
            return QMessageBox.warning(self, 'Предупреждение',
                                       'Удаление происходит на вкладках таблиц!')

        current_row = table.currentRow()
        if current_row < 0:
            return QMessageBox.warning(self, 'Предупреждение', 'Выберите запись для удаления')

        button = QMessageBox.question(
            self,
            'Подтверждение',
            'Вы уверены, что хотите удалить выделенную строку?',
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No
        )

        if button == QMessageBox.StandardButton.Yes:
            if table == self.tableEmployees:
                if not doc.docDismissal(table.item(current_row, 0).text(), table.item(current_row, 1).text(),
                                        table.item(current_row, 2).text(), str(date.today().strftime('%d.%m.%Y')),
                                        table.item(current_row, 5).text()):
                    return QMessageBox.critical(self, 'Ошибка',
                                                'Уберите существующий приказ об увольнении из папки "Документы"')
                db.deleteEmployee(table.item(current_row, 0).text(), table.item(current_row, 3).text(),
                                  table.item(current_row, 4).text(), str(date.today().strftime('%d.%m.%Y')))
                db.insertLog("Удаление сотрудника " + table.item(current_row, 0).text(),
                             str(datetime.now().time().strftime("%H:%M:%S")) + " | " + str(
                                 date.today().strftime('%d.%m.%Y')), current_user)
            elif table == self.tableInterns:
                db.deleteIntern(table.item(current_row, 0).text(), table.item(current_row, 3).text(),
                                table.item(current_row, 4).text(), str(date.today().strftime('%d.%m.%Y')))
                db.insertLog("Удаление стажера " + table.item(current_row, 0).text(),
                             str(datetime.now().time().strftime("%H:%M:%S")) + " | " + str(
                                 date.today().strftime('%d.%m.%Y')),
                             current_user)
            table.removeRow(current_row)
            if table.rowCount() <= 0:
                table.hide()
                txt.show()
            QMessageBox.information(self, 'Успешно', 'Строка была успешно удалена!')

    def acceptRow(self):
        if self.tab.currentIndex() != 1:
            return QMessageBox.warning(self, 'Предупреждение',
                                       'Принятие на работу осуществляется только для стажеров!')

        current_row = self.tableInterns.currentRow()
        if current_row < 0:
            return QMessageBox.warning(self, 'Предупреждение', 'Выберите запись для перемещения')

        button = QMessageBox.question(
            self,
            'Подтверждение',
            'Вы уверены, что хотите переместить выделенную строку?',
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No
        )

        if button == QMessageBox.StandardButton.Yes:
            if not doc.docHiring(self.tableInterns.item(current_row, 0).text(),
                                 self.tableInterns.item(current_row, 1).text(),
                                 self.tableInterns.item(current_row, 2).text(), str(date.today().strftime('%d.%m.%Y')),
                                 self.tableInterns.item(current_row, 5).text(),
                                 str(db.getSalaryByProfession(self.tableInterns.item(current_row, 5).text())), self.tableInterns.item(current_row, 6).text()):
                return QMessageBox.critical(self, 'Ошибка',
                                            'Уберите существующий приказ о зачислении из папки "Документы"')
            db.acceptIntern(self.tableInterns.item(current_row, 0).text(),
                            self.tableInterns.item(current_row, 3).text(),
                            self.tableInterns.item(current_row, 4).text(), str(date.today().strftime('%d.%m.%Y')))
            db.insertLog("Перемещение стажера " + self.tableInterns.item(current_row, 0).text(),
                         str(datetime.now().time().strftime("%H:%M:%S")) + " | " + str(
                             date.today().strftime('%d.%m.%Y')),
                         current_user)

            row = self.tableEmployees.rowCount()
            self.tableEmployees.insertRow(row)
            self.tableEmployees.setItem(row, 0, QTableWidgetItem(self.tableInterns.item(current_row, 0).text()))
            self.tableEmployees.setItem(row, 1, QTableWidgetItem(self.tableInterns.item(current_row, 1).text()))
            self.tableEmployees.setItem(row, 2, QTableWidgetItem(self.tableInterns.item(current_row, 2).text()))
            self.tableEmployees.setItem(row, 3, QTableWidgetItem(self.tableInterns.item(current_row, 3).text()))
            self.tableEmployees.setItem(row, 4, QTableWidgetItem(self.tableInterns.item(current_row, 4).text()))
            self.tableEmployees.setItem(row, 5, QTableWidgetItem(self.tableInterns.item(current_row, 5).text()))
            self.tableEmployees.setItem(row, 6, QTableWidgetItem(self.tableInterns.item(current_row, 6).text()))
            self.tableEmployees.setItem(row, 7, QTableWidgetItem(self.tableInterns.item(current_row, 7).text()))

            self.lblEmp.hide()
            self.tableEmployees.show()

            self.tableInterns.removeRow(current_row)
            if self.tableInterns.rowCount() <= 0:
                self.tableInterns.hide()
                self.lblInterns.show()
            QMessageBox.information(self, 'Успешно', 'Строка была успешно перемещена!')

    def toEditWindow(self):
        global editWindow

        if self.tab.currentIndex() == 0:
            table = self.tableEmployees
            tbl = 0
        elif self.tab.currentIndex() == 1:
            table = self.tableInterns
            tbl = 1
        else:
            return QMessageBox.warning(self, 'Предупреждение',
                                       'Изменение возможно только для таблиц!')

        current_row = table.currentRow()
        if current_row < 0:
            return QMessageBox.warning(self, 'Предупреждение', 'Выберите запись для изменения')

        row = []

        for i in range(8):
            row.append(table.item(current_row, i).text())

        editWindow = None
        editWindow = EditWindow(self, row, tbl)

    def addRow(self):
        if not self.valid():
            return

        position = self.position.currentIndex() + 1
        workplace = self.workplace.currentIndex() + 1
        today = str(date.today().strftime('%d.%m.%Y'))

        if self.tableBox.currentIndex() == 0:
            table = self.tableEmployees
            txt = self.lblEmp
            if not doc.docHiring(self.last_name.text().strip(), self.first_name.text().strip(),
                                 self.middle_name.text().strip(), today,
                                 self.position.currentText(),
                                 str(db.getSalaryByProfession(self.position.currentText())), self.workplace.currentText()):
                return QMessageBox.critical(self, 'Ошибка',
                                            'Уберите существующий приказ о зачислении из папки "Документы"')
            if db.insertEmployee(self.last_name.text().strip(), self.first_name.text().strip(),
                                 self.middle_name.text().strip(),
                                 self.phone.text().strip(), self.email.text().strip(), position,
                                 self.experience.text().strip(), workplace, today):
                QMessageBox.information(self, 'Успешно', 'Новый сотрудник успешно добавлен!')
                db.insertLog("Добавление сотрудника " + self.last_name.text().strip(),
                             str(datetime.now().time().strftime("%H:%M:%S")) + " | " + str(
                                 date.today().strftime('%d.%m.%Y')),
                             current_user)
            else:
                QMessageBox.critical(self, 'Ошибка', 'Данный сотрудник уже есть в базе данных!')

        elif self.tableBox.currentIndex() == 1:
            table = self.tableInterns
            txt = self.lblInterns
            if db.insertIntern(self.last_name.text().strip(), self.first_name.text().strip(),
                               self.middle_name.text().strip(),
                               self.phone.text().strip(), self.email.text().strip(), position,
                               self.experience.text().strip(), workplace, today):
                QMessageBox.information(self, 'Успешно', 'Новый стажер успешно добавлен!')
                db.insertLog("Добавление стажера " + self.last_name.text().strip(),
                             str(datetime.now().time().strftime("%H:%M:%S")) + " | " + str(
                                 date.today().strftime('%d.%m.%Y')),
                             current_user)
            else:
                QMessageBox.critical(self, 'Ошибка', 'Данный стажер уже есть в базе данных!')
        else:
            return 0

        row = table.rowCount()
        table.insertRow(row)
        table.setItem(row, 0, QTableWidgetItem(self.last_name.text().strip()))
        table.setItem(row, 1, QTableWidgetItem(self.first_name.text().strip()))
        table.setItem(row, 2, QTableWidgetItem(self.middle_name.text().strip()))
        table.setItem(row, 3, QTableWidgetItem(self.phone.text().strip()))
        table.setItem(row, 4, QTableWidgetItem(self.email.text().strip()))
        table.setItem(row, 5, QTableWidgetItem(str(db.selectPositionById(position)[0])))
        table.setItem(row, 6, QTableWidgetItem(self.experience.text().strip()))
        table.setItem(row, 7, QTableWidgetItem(str(db.selectWorkplaceById(workplace)[0])))

        txt.hide()
        table.show()

        self.resetForm()

    def addUser(self):
        if not self.validUser():
            return

        if db.insertUser(self.loginForm.text().strip(), self.passwordForm.text().strip(),
                         self.codewordForm.text().strip().upper()):
            QMessageBox.information(self, 'Успешно', 'Новый пользователь успешно добавлен!')
            db.insertLog("Добавление пользователя " + self.loginForm.text().strip(),
                         str(datetime.now().time().strftime("%H:%M:%S")) + " | " + str(
                             date.today().strftime('%d.%m.%Y')),
                         current_user)

        self.resetFormUser()

    def getEmpTable(self, employees):
        self.tableEmployees.setRowCount(len(employees))

        row = 0
        for e in employees:
            self.tableEmployees.setItem(row, 0, QTableWidgetItem(e[1]))
            self.tableEmployees.setItem(row, 1, QTableWidgetItem(e[2]))
            self.tableEmployees.setItem(row, 2, QTableWidgetItem(e[3]))
            self.tableEmployees.setItem(row, 3, QTableWidgetItem(e[4]))
            self.tableEmployees.setItem(row, 4, QTableWidgetItem(e[5]))
            self.tableEmployees.setItem(row, 5, QTableWidgetItem(str(db.selectPositionById(e[6])[0])))
            self.tableEmployees.setItem(row, 6, QTableWidgetItem(str(e[7])))
            self.tableEmployees.setItem(row, 7, QTableWidgetItem(str(db.selectWorkplaceById(e[8])[0])))
            row += 1

    def getIntTable(self, interns):
        self.tableInterns.setRowCount(len(interns))

        row = 0
        for i in interns:
            self.tableInterns.setItem(row, 0, QTableWidgetItem(i[1]))
            self.tableInterns.setItem(row, 1, QTableWidgetItem(i[2]))
            self.tableInterns.setItem(row, 2, QTableWidgetItem(i[3]))
            self.tableInterns.setItem(row, 3, QTableWidgetItem(i[4]))
            self.tableInterns.setItem(row, 4, QTableWidgetItem(i[5]))
            self.tableInterns.setItem(row, 5, QTableWidgetItem(str(db.selectPositionById(i[6])[0])))
            self.tableInterns.setItem(row, 6, QTableWidgetItem(str(i[7])))
            self.tableInterns.setItem(row, 7, QTableWidgetItem(str(db.selectWorkplaceById(i[8])[0])))
            row += 1

    def clearTable(self, table):
        while table.rowCount() > 0:
            table.removeRow(0)

    def getEmployees(self, msg):
        log = db.selectEmployeesBy(msg)
        l = len(log)
        if l > 0:
            self.clearTable(self.tableEmployees)
            self.tableEmployees.setRowCount(l)

            row = 0
            for i in log:
                self.tableEmployees.setItem(row, 0, QTableWidgetItem(i[1]))
                self.tableEmployees.setItem(row, 1, QTableWidgetItem(i[2]))
                self.tableEmployees.setItem(row, 2, QTableWidgetItem(i[3]))
                self.tableEmployees.setItem(row, 3, QTableWidgetItem(i[4]))
                self.tableEmployees.setItem(row, 4, QTableWidgetItem(i[5]))
                self.tableEmployees.setItem(row, 5, QTableWidgetItem(str(db.selectPositionById(i[6])[0])))
                self.tableEmployees.setItem(row, 6, QTableWidgetItem(str(i[7])))
                self.tableEmployees.setItem(row, 7, QTableWidgetItem(str(db.selectWorkplaceById(i[8])[0])))
                row += 1
            return 0
        QMessageBox.critical(self, 'Ошибка', 'Нет таких сотрудников!')

    def getInterns(self, msg):
        log = db.selectInternsBy(msg)
        l = len(log)
        if l > 0:
            self.clearTable(self.tableInterns)
            self.tableInterns.setRowCount(l)

            row = 0
            for i in log:
                self.tableInterns.setItem(row, 0, QTableWidgetItem(i[1]))
                self.tableInterns.setItem(row, 1, QTableWidgetItem(i[2]))
                self.tableInterns.setItem(row, 2, QTableWidgetItem(i[3]))
                self.tableInterns.setItem(row, 3, QTableWidgetItem(i[4]))
                self.tableInterns.setItem(row, 4, QTableWidgetItem(i[5]))
                self.tableInterns.setItem(row, 5, QTableWidgetItem(str(db.selectPositionById(i[6])[0])))
                self.tableInterns.setItem(row, 6, QTableWidgetItem(str(i[7])))
                self.tableInterns.setItem(row, 7, QTableWidgetItem(str(db.selectWorkplaceById(i[8])[0])))
                row += 1
            return 0
        QMessageBox.critical(self, 'Ошибка', 'Нет таких стажеров!')

    def validUser(self):
        login = self.loginForm.text().strip()
        password = self.passwordForm.text().strip()
        codeword = self.codewordForm.text().strip()

        if not login:
            QMessageBox.critical(self, 'Ошибка', 'Введите логин!')
            self.loginForm.setFocus()
            return False

        if not password:
            QMessageBox.critical(self, 'Ошибка', 'Введите пароль!')
            self.passwordForm.setFocus()
            return False

        if not codeword:
            QMessageBox.critical(self, 'Ошибка', 'Введите кодовое слово!')
            self.codewordForm.setFocus()
            return False

        if len(codeword) != 6:
            QMessageBox.critical(self, 'Ошибка', 'Кодовое слово должно быть из 6-ти символов!')
            self.codewordForm.setFocus()
            return False

        return True

    def valid(self):
        first_name = self.first_name.text().strip()
        last_name = self.last_name.text().strip()
        phone = self.phone.text().strip()
        email = self.email.text().strip()

        if not first_name:
            QMessageBox.critical(self, 'Ошибка', 'Введите имя!')
            self.first_name.setFocus()
            return False

        if not last_name:
            QMessageBox.critical(self, 'Ошибка', 'Введите фамилию!')
            self.last_name.setFocus()
            return False

        if not phone:
            QMessageBox.critical(self, 'Ошибка', 'Введите номер телефона!')
            self.phone.setFocus()
            return False

        if not match(r'^\+?[1-9]\d{1,14}$', phone) or not len(phone) >= 7 or not len(phone) <= 15:
            QMessageBox.critical(self, 'Ошибка', 'Некорректный формат номера телефона!')
            self.phone.setFocus()
            return False

        if not phone.startswith("8") and not phone.startswith("7") and not phone.startswith("+7"):
            QMessageBox.critical(self, 'Ошибка', 'Некорректный формат номера телефона!')
            self.phone.setFocus()
            return False

        if not match(r"^[\w\.\+\-]+\@[\w]+\.[a-z]{2,3}$", email):
            QMessageBox.critical(self, 'Ошибка', 'Некорректный формат почты!')
            self.email.setFocus()
            return False

        try:
            experience = int(self.experience.text().strip())
        except ValueError:
            QMessageBox.critical(self, 'Ошибка', 'Недопустимое значение опыта!')
            self.experience.setFocus()
            return False

        if experience < 0 or experience > 150:
            QMessageBox.critical(self, 'Ошибка', 'Недопустимое значение опыта!')
            self.experience.setFocus()
            return False

        return True

    def resetFormUser(self):
        self.loginForm.clear()
        self.passwordForm.clear()
        self.codewordForm.clear()

        self.show()

    def resetForm(self):
        self.first_name.clear()
        self.last_name.clear()
        self.middle_name.clear()
        self.phone.clear()
        self.email.clear()
        self.experience.clear()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    loginWindow = LoginWindow()
    sys.exit(app.exec())

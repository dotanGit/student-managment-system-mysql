import sys
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QLabel, \
     QWidget, QGridLayout, QLineEdit, QPushButton, QMainWindow, \
     QTableWidget, QTableWidgetItem, QDialog, QComboBox, QToolBar, \
     QStatusBar, QMessageBox
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt
import mysql.connector

class DatabaseConnection:
    def __init__(self, host="localhost", user="root", password='Enter Password here', database='school'):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def connect(self):
        connection = mysql.connector.connect(host=self.host, user=self.user, password=self.password, database=self.database)
        return connection


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set window title and minimum size
        self.setWindowTitle("Student Management System")
        self.setMinimumSize(600, 400)

        # Create menu bar and add menu items
        file_menu_item = self.menuBar().addMenu("&File")
        help_menu_item = self.menuBar().addMenu("&Help")
        edit_menu_item = self.menuBar().addMenu("&Edit")

        # Add "Add Student" action to "File" menu and toolbar
        add_student_action = QAction(QIcon("icons/add.png"), "Add Student", self)
        add_student_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_student_action)

        # Add "About" action to "Help" menu
        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)
        about_action.triggered.connect(self.about)

        # Add "Search" action to "Edit" menu and toolbar
        search_action = QAction(QIcon("icons/search.png"), "Search", self)
        edit_menu_item.addAction(search_action)
        search_action.triggered.connect(self.search)

        # Create a table to display data
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("Id", "Name", "Course", "Mobile"))
        self.table.verticalHeader().setVisible(
            False)  # Remove the numbering of the table, because there's ID in the data
        self.setCentralWidget(self.table)

        # Create a toolbar and add toolbar elements
        toolbar = QToolBar()
        toolbar.setMovable(True)  # Allow user to move the toolbar around
        self.addToolBar(toolbar)

        toolbar.addAction(add_student_action)
        toolbar.addAction(search_action)

        # Create a status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Connect cellClicked signal to cell_clicked method
        self.table.cellClicked.connect(self.cell_clicked)

    def cell_clicked(self):
        # Create "Edit Record" and "Delete Record" buttons and connect them to their respective methods
        edit_button = QPushButton("Edit Record")
        edit_button.clicked.connect(self.edit)

        delete_button = QPushButton("Delete Record")
        delete_button.clicked.connect(self.delete)

        # Delete existing buttons from the status bar to prevent duplicates
        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.status_bar.removeWidget(child)

        # Add "Edit Record" and "Delete Record" buttons to the status bar
        self.status_bar.addWidget(edit_button)
        self.status_bar.addWidget(delete_button)

    def load_data(self):
        # Connect to the database and retrieve data
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM students")
        result = cursor.fetchall()

        # Clear the table to prevent duplicate data and start adding new rows from index 0
        self.table.setRowCount(0)

        # Add each row of data to the table
        for row_number, row_data in enumerate(result):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

        # Close the database connection
        connection.close()

    def insert(self):
        # Open the insert dialog
        dialog = InsertDialog()
        dialog.exec()

    def search(self):
        # Open the search dialog
        dialog = SearchDialog()
        dialog.exec()

    def edit(self):
        # Open the edit dialog
        dialog = EditDialog()
        dialog.exec()

    def delete(self):
        # Open the delete dialog
        dialog = DeleteDialog()
        dialog.exec()

    def about(self):
        # Open the about dialog
        dialog = AboutDialog()
        dialog.exec()


class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        content = """
        About This App
        ______________

        This app was created as part of my projects portfolio, 
        this is simple student data base structure which is 
        user friendly to manage and use
        """
        self.setText(content)


class EditDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Update Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Getting the name of the selected student when its clicked
        index = main_window.table.currentRow()
        student_name = main_window.table.item(index,
                                              1).text()  # index is the row number and 1 is the columns which in our database is the name columns

        # Get id from selected row
        self.student_id = main_window.table.item(index, 0).text()

        # Add student name widget
        self.student_name = QLineEdit(student_name)
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Add combo box of courses
        course = main_window.table.item(index, 2).text()
        self.course = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.course.addItems(courses)
        self.course.setCurrentText(course)
        layout.addWidget(self.course)

        # Add student phone number
        mobile = main_window.table.item(index, 3).text()
        self.mobile = QLineEdit(mobile)
        self.mobile.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile)

        # Add submit button
        button = QPushButton("Update")
        button.clicked.connect(self.update_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def update_student(self):
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("UPDATE students SET name = %s, course = %s, mobile = %s WHERE id = %s",
                       (self.student_name.text(),
                        self.course.itemText(self.course.currentIndex()),
                        self.mobile.text(),
                        self.student_id))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()


class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Delete Student Data")

        # Get the index of the selected row
        self.index = main_window.table.currentRow()

        # Get the name of the selected student
        student_name = main_window.table.item(self.index, 1).text()

        layout = QGridLayout()

        # Add a confirmation message
        confirmation = QLabel(f'Are you sure you want to delete "{student_name}" account?')
        layout.addWidget(confirmation, 0, 0, 1, 2)

        # Add "Yes" and "No" buttons
        yes = QPushButton("Yes")
        no = QPushButton("No")
        layout.addWidget(yes, 1, 0)
        layout.addWidget(no, 1, 1)

        self.setLayout(layout)

        # Connect the "Yes" button to the delete_student method
        yes.clicked.connect(self.delete_student)

    def delete_student(self):
        # Get the id of the selected student
        student_id = main_window.table.item(self.index, 0).text()

        # Connect to the database and execute the delete query
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("DELETE from students WHERE id = %s", (student_id,))
        connection.commit()
        cursor.close()
        connection.close()

        # Reload the data in the main window table
        main_window.load_data()

        # Close the dialog box
        self.close()

        # Display a success message using QMessageBox
        confirmation_deleted = QMessageBox()
        confirmation_deleted.setWindowTitle("Success")
        confirmation_deleted.setText("The record was deleted successfully!")
        confirmation_deleted.exec()


class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Insert Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Add student name widget
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Add combo box of courses
        self.course = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.course.addItems(courses)
        layout.addWidget(self.course)

        # Add student phone number
        self.mobile = QLineEdit()
        self.mobile.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile)

        # Add submit button
        button = QPushButton("Submit")
        button.clicked.connect(self.add_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def add_student(self):
        # Get values entered by user
        name = self.student_name.text()
        course = self.course.itemText(self.course.currentIndex())
        mobile = self.mobile.text()

        # Connect to database and execute SQL query to insert new student data
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO students (name, course, mobile) VALUES (%s, %s, %s)",
                       (name, course, mobile))

        # Commit the changes and close the connection to the database
        connection.commit()
        cursor.close()
        connection.close()

        # Refresh the data displayed in the main window to show the new student added
        main_window.load_data()


class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()
        # Set Window Title and Size
        self.setWindowTitle("Search Student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        # Create Layout and input widgets
        layout = QVBoxLayout()
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Add submit button
        button = QPushButton("Search")
        button.clicked.connect(self.search)
        layout.addWidget(button)

        self.setLayout(layout)

    def search(self):
        name = self.student_name.text()  # grabs the name that the user entered
        connection = DatabaseConnection().connect()  # connect to the database
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM students WHERE name = %s", (name,))  # we select all the rows where the name is equal to the name
        result = cursor.fetchall()
        rows = list(result)  # the result is a generator, so we convert them into a list
        items = main_window.table.findItems(name, Qt.MatchFlag.MatchFixedString)
        for item in items:
            main_window.table.item(item.row(), 1).setSelected(True)

        cursor.close()
        connection.close()


app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
main_window.load_data()
sys.exit(app.exec())

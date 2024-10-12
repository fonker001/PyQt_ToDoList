# main.py
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QListWidget, QLineEdit, QHBoxLayout, QComboBox, QDateEdit, QLabel, QProgressBar, QMenuBar, QInputDialog, QMenu
from PyQt6.QtCore import Qt, QDate, QTimer
from PyQt6.QtGui import QAction, QIcon
from plyer import notification
from datetime import datetime
from todo_manager import ToDoManager
from persistence_manager import PersistenceManager

class ToDoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("To-Do List")
        self.setWindowIcon(QIcon("icon.png"))

        self.menu_bar = QMenuBar(self)
        self.setMenuBar(self.menu_bar)
        self.theme_menu = self.menu_bar.addMenu("Themes")
        
        self.light_action = QAction("Light Mode", self)
        self.light_action.triggered.connect(lambda: self.load_stylesheet("light.qss"))
        self.theme_menu.addAction(self.light_action)
        
        self.dark_action = QAction("Dark Mode", self)
        self.dark_action.triggered.connect(lambda: self.load_stylesheet("dark.qss"))
        self.theme_menu.addAction(self.dark_action)

        self.category_menu = self.menu_bar.addMenu("Categories")
        
        self.add_category_action = QAction("Add Category", self)
        self.add_category_action.triggered.connect(self.add_category)
        self.category_menu.addAction(self.add_category_action)
        
        self.delete_category_action = QAction("Delete Category", self)
        self.delete_category_action.triggered.connect(self.delete_category)
        self.category_menu.addAction(self.delete_category_action)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search tasks...")
        self.search_input.textChanged.connect(self.search_todos)
        self.layout.addWidget(self.search_input)

        self.todo_list = QListWidget()
        self.todo_list.itemChanged.connect(self.update_progress)
        self.todo_list.itemDoubleClicked.connect(self.edit_todo)
        self.todo_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.todo_list.customContextMenuRequested.connect(self.show_context_menu)
        self.todo_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)  # Add this line
        self.layout.addWidget(self.todo_list)

        self.todo_input = QLineEdit()
        self.layout.addWidget(self.todo_input)

        self.recurrence_combo = QComboBox()
        self.recurrence_combo.addItems(["None", "Daily", "Weekly", "Monthly"])
        self.layout.addWidget(self.recurrence_combo)

        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["Low", "Medium", "High"])
        self.layout.addWidget(self.priority_combo)

        self.due_date_edit = QDateEdit(calendarPopup=True)
        self.due_date_edit.setDate(QDate.currentDate())
        self.layout.addWidget(self.due_date_edit)

        self.category_combo = QComboBox()
        self.category_combo.addItems(["General", "Work", "Personal", "Errands"])
        self.layout.addWidget(self.category_combo)

        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Add To-Do")
        self.add_button.clicked.connect(self.add_todo)
        button_layout.addWidget(self.add_button)

        self.delete_button = QPushButton("Delete To-Do")
        self.delete_button.clicked.connect(self.delete_todo)
        button_layout.addWidget(self.delete_button)
        
        self.layout.addLayout(button_layout)

        self.progress_bar = QProgressBar()
        self.layout.addWidget(self.progress_bar)

        self.todo_manager = ToDoManager(self.todo_list)
        self.persistence_manager = PersistenceManager()

        self.load_todos(self.persistence_manager.load_todos())
        self.update_progress()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_reminders)
        self.timer.start(60000)  # Check every minute

        self.setGeometry(100, 100, 800, 600)  # Set initial window size and position

        self.load_stylesheet("light.qss")  # Load default theme

    def load_stylesheet(self, filename):
        with open(filename, "r") as f:
            self.setStyleSheet(f.read())

    def add_category(self):
        text, ok = QInputDialog.getText(self, 'Add Category', 'Enter category name:')
        if ok and text:
            self.category_combo.addItem(text)

    def delete_category(self):
        current_text = self.category_combo.currentText()
        index = self.category_combo.findText(current_text)
        if index != -1:
            self.category_combo.removeItem(index)

    def add_todo(self):
        todo = self.todo_input.text()
        priority = self.priority_combo.currentText()
        due_date = self.due_date_edit.date().toString('yyyy-MM-dd')
        category = self.category_combo.currentText()
        recurrence = self.recurrence_combo.currentText()
        self.todo_manager.add_todo(todo, priority, due_date, category, recurrence)
        self.todo_input.clear()
        self.update_progress()

    def delete_todo(self):
        self.todo_manager.delete_selected_todos()
        self.update_progress()

    def edit_todo(self, item):
        text, ok = QInputDialog.getText(self, 'Edit To-Do', 'Edit task:', text=item.text())
        if ok and text:
            item.setText(text)

    def load_todos(self, todos):
        self.todo_manager.load_todos(todos)


    def closeEvent(self, event):
        todos = self.todo_manager.get_all_todos()
        self.persistence_manager.save_todos(todos)
        event.accept()

    def get_all_todos(self):
        todos = []
        for index in range(self.todo_list.count()):
            item = self.todo_list.item(index)
            text = item.text()
            subtasks = item.data(Qt.ItemDataRole.UserRole)
            todos.append(f"{text} | subtasks:{','.join(subtasks)}")
        return todos

    def search_todos(self, text):
        for index in range(self.todo_list.count()):
            item = self.todo_list.item(index)
            item.setHidden(text.lower() not in item.text().lower())

    def show_context_menu(self, position):
        menu = QMenu()
        add_subtask_action = QAction("Add Subtask", self)
        add_subtask_action.triggered.connect(self.add_subtask)
        menu.addAction(add_subtask_action)
        menu.exec(self.todo_list.mapToGlobal(position))

    def add_subtask(self):
        item = self.todo_list.currentItem()
        if item:
            text, ok = QInputDialog.getText(self, 'Add Subtask', 'Enter subtask:')
            if ok and text:
                self.todo_manager.add_subtask(item, text)
                self.update_subtasks(item)

    def update_subtasks(self, item):
        subtasks = item.data(Qt.ItemDataRole.UserRole)
        task_text = item.text().split(" | ")[-1]
        new_text = f"{task_text}\n" + "\n".join(f"  - {subtask}" for subtask in subtasks)
        item.setText(new_text)

    def update_progress(self):
        completed = self.todo_manager.get_completed_count()
        total = self.todo_manager.get_total_count()
        if total > 0:
            progress = int((completed / total) * 100)
        else:
            progress = 0
        self.progress_bar.setValue(progress)

    def check_reminders(self):
        current_date = QDate.currentDate().toString('yyyy-MM-dd')
        for index in range(self.todo_list.count()):
            item = self.todo_list.item(index)
            if current_date in item.text():
                self.show_notification("Task Reminder", f"Task due today: {item.text()}")

    def show_notification(self, title, message):
        notification.notify(
            title=title,
            message=message,
            timeout=10
        )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    with open("light.qss", "r") as f:
        app.setStyleSheet(f.read())
    
    window = ToDoApp()
    window.show()
    sys.exit(app.exec())

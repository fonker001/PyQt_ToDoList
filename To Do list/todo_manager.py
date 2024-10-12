# todo_manager.py
from PyQt6.QtWidgets import QListWidget, QListWidgetItem
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

class ToDoManager:
    def __init__(self, todo_list: QListWidget):
        self.todo_list = todo_list

    def add_todo(self, todo: str, priority: str, due_date: str, category: str, recurrence: str = "None", subtasks=None):
        if todo:
            item = QListWidgetItem(f"{category} | {priority} | {due_date} | {recurrence} | {todo}")
            item.setCheckState(Qt.CheckState.Unchecked)
            item.setData(Qt.ItemDataRole.UserRole, subtasks or [])
            self.todo_list.addItem(item)
            self.set_priority_color(item, priority)

    def add_subtask(self, parent_item, subtask: str):
        subtasks = parent_item.data(Qt.ItemDataRole.UserRole)
        subtasks.append(subtask)
        parent_item.setData(Qt.ItemDataRole.UserRole, subtasks)

    def delete_selected_todos(self):
        for item in self.todo_list.selectedItems():
            self.todo_list.takeItem(self.todo_list.row(item))

    def get_all_todos(self):
        return [self.todo_list.item(index).text() for index in range(self.todo_list.count())]

    def load_todos(self, todos):
        for todo in todos:
            parts = todo.split(" | ")
            category = parts[0] if len(parts) > 1 else "General"
            priority = parts[1] if len(parts) > 2 else "Low"
            due_date = parts[2] if len(parts) > 3 else ""
            recurrence = parts[3] if len(parts) > 4 else "None"
            self.add_todo(parts[-1], priority, due_date, category, recurrence)

    def get_completed_count(self):
        return sum(1 for index in range(self.todo_list.count()) if self.todo_list.item(index).checkState() == Qt.CheckState.Checked)

    def get_total_count(self):
        return self.todo_list.count()

    def set_priority_color(self, item: QListWidgetItem, priority: str):
        if priority == "High":
            item.setForeground(QColor(255, 0, 0))  # Red
        elif priority == "Medium":
            item.setForeground(QColor(255, 165, 0))  # Orange
        else:
            item.setForeground(QColor(0, 128, 0))  # Green

# persistence_manager.py
import os

class PersistenceManager:
    def __init__(self, file_path='todos.txt'):
        self.file_path = file_path

    def save_todos(self, todos):
        with open(self.file_path, 'w') as file:
            for todo in todos:
                file.write(todo + '\n')

    def load_todos(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as file:
                return [line.strip() for line in file.readlines()]
        return []

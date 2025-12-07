from pydantic import BaseModel
from typing import List
import uuid

class Todo(BaseModel):
    id: str
    title: str
    completed: bool = False

class TodoDB:
    def __init__(self):
        self.todos: List[Todo] = []

    def create(self, title: str) -> Todo:
        todo = Todo(id=str(uuid.uuid4()), title=title)
        self.todos.append(todo)
        return todo

    def list(self) -> List[Todo]:
        return self.todos

    def toggle(self, todo_id: str) -> Todo | None:
        for todo in self.todos:
            if todo.id == todo_id:
                todo.completed = not todo.completed
                return todo
        return None

    def delete(self, todo_id: str) -> bool:
        for i, todo in enumerate(self.todos):
            if todo.id == todo_id:
                self.todos.pop(i)
                return True
        return False

db = TodoDB()
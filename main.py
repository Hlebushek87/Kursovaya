from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from database import db, Todo
from pydantic import BaseModel
from fastapi.responses import FileResponse

app = FastAPI(title="Моё To-Do приложение")

@app.get("/")
def root():
    return FileResponse("static/index.html")

# Теперь статические файлы отдаются с корня сайта
app.mount("/static", StaticFiles(directory="static"), name="static")

class TodoCreate(BaseModel):
    title: str

# API
@app.post("/api/todos", response_model=Todo)
async def create_todo(todo: TodoCreate):
    return db.create(todo.title)

@app.get("/api/todos", response_model=list[Todo])
async def get_todos():
    return db.list()

@app.put("/api/todos/{todo_id}/toggle", response_model=Todo)
async def toggle_todo(todo_id: str):
    todo = db.toggle(todo_id)
    if not todo:
        raise HTTPException(404, "Задача не найдена")
    return todo

@app.delete("/api/todos/{todo_id}")
async def delete_todo(todo_id: str):
    if not db.delete(todo_id):
        raise HTTPException(404, "Задача не найдена")
    return JSONResponse(status_code=200, content={"detail": "Удалено"})


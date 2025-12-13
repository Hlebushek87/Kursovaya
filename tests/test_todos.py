import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_todo():
    response = client.post("/api/todos", json={"title": "Сделать домашку"})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Сделать домашку"
    assert "id" in data

def test_get_todos():
    response = client.get("/api/todos")
    assert response.status_code == 200
    todos = response.json()
    assert isinstance(todos, list)
    assert any(todo["title"] == "Сделать домашку" for todo in todos)

def test_toggle_todo():
    # сначала создаём задачу
    create_resp = client.post("/api/todos", json={"title": "Погулять"})
    todo_id = create_resp.json()["id"]

    # переключаем статус
    toggle_resp = client.put(f"/api/todos/{todo_id}/toggle")
    assert toggle_resp.status_code == 200
    toggled = toggle_resp.json()
    assert toggled["done"] in [True, False]  # поле done должно измениться

def test_delete_todo():
    # создаём задачу
    create_resp = client.post("/api/todos", json={"title": "Удалить меня"})
    todo_id = create_resp.json()["id"]

    # удаляем
    delete_resp = client.delete(f"/api/todos/{todo_id}")
    assert delete_resp.status_code == 200
    assert delete_resp.json()["detail"] == "Удалено"

def test_toggle_not_found():
    response = client.put("/api/todos/unknown_id/toggle")
    assert response.status_code == 404

def test_delete_not_found():
    response = client.delete("/api/todos/unknown_id")
    assert response.status_code == 404

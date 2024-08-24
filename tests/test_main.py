import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert "<title>Todo App</title>" in response.text

def test_add_todo():
    response = client.post("/add", data={"task": "Test task"})
    assert response.status_code == 200
    assert "Test task" in response.text

def test_update_todo():
    # First, add a todo
    client.post("/add", data={"task": "Update test task"})
    
    # Then, update it
    response = client.get("/")
    todos = response.context["todos"]
    todo_id = todos[-1]["id"]
    response = client.post(f"/update/{todo_id}", data={"done": "true"})
    assert response.status_code == 200

    # Verify the update
    response = client.get("/")
    updated_todo = next((todo for todo in response.context["todos"] if todo["id"] == todo_id), None)
    assert updated_todo["done"] == "true"

def test_delete_todo():
    # First, add a todo
    client.post("/add", data={"task": "Delete test task"})
    
    # Then, delete it
    response = client.get("/")
    todos = response.context["todos"]
    todo_id = todos[-1]["id"]
    response = client.post(f"/delete/{todo_id}")
    assert response.status_code == 200

    # Verify the deletion
    response = client.get("/")
    assert not any(todo["id"] == todo_id for todo in response.context["todos"])
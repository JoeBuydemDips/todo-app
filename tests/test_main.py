import sys
import os
import json

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

def test_add_empty_todo():
    response = client.post("/add", data={"task": ""})
    assert response.status_code == 422  # Unprocessable Entity

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

def test_update_nonexistent_todo():
    response = client.post("/update/nonexistent-id", data={"done": "true"})
    assert response.status_code == 404

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

def test_delete_nonexistent_todo():
    response = client.post("/delete/nonexistent-id")
    assert response.status_code == 404

def test_get_todos():
    # Clear existing todos
    response = client.get("/")
    todos = response.context["todos"]
    for todo in todos:
        client.post(f"/delete/{todo['id']}")

    # Add some test todos
    tasks = ["Task 1", "Task 2", "Task 3"]
    for task in tasks:
        client.post("/add", data={"task": task})

    # Get todos
    response = client.get("/")
    assert response.status_code == 200
    todos = response.context["todos"]
    assert len(todos) == len(tasks)
    for i, todo in enumerate(todos):
        assert todo["task"] == tasks[i]

def test_static_files():
    css_response = client.get("/static/styles.css")
    assert css_response.status_code == 200
    assert "text/css" in css_response.headers["content-type"]

    js_response = client.get("/static/script.js")
    assert js_response.status_code == 200
    # Update this line to accept both MIME types
    assert any(mime_type in js_response.headers["content-type"] for mime_type in ["application/javascript", "text/javascript", "text/javascript; charset=utf-8"])

def test_clear_todos():
    # Add some test todos
    tasks = ["Task 1", "Task 2", "Task 3"]
    for task in tasks:
        client.post("/add", data={"task": task})

    # Clear todos
    response = client.post("/clear")
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "success"
    assert len(result["todos"]) == 0

    # Verify that todos are cleared
    response = client.get("/")
    assert response.status_code == 200
    todos = response.context["todos"]
    assert len(todos) == 0

def test_undo_action():
    # Clear todos
    client.post("/clear")

    # Add a todo
    client.post("/add", data={"task": "Test undo"})

    # Undo the add action
    response = client.post("/undo")
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "success"
    assert len(result["todos"]) == 0

    # Add two todos
    client.post("/add", data={"task": "Task 1"})
    client.post("/add", data={"task": "Task 2"})

    # Delete the second todo
    response = client.get("/")
    todos = response.context["todos"]
    todo_id = todos[-1]["id"]
    client.post(f"/delete/{todo_id}")

    # Undo the delete action
    response = client.post("/undo")
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "success"
    assert len(result["todos"]) == 2
    assert result["todos"][-1]["task"] == "Task 2"

    response = client.post("/clear")
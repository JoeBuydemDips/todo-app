from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import csv
import uuid
import copy
import os
from functools import lru_cache

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Use an environment variable to set the database file path, defaulting to "todos.csv"
DEFAULT_DB_FILE = "todos.csv"

@lru_cache()
def get_db_file():
    return os.environ.get("TODO_DB_FILE", DEFAULT_DB_FILE)

# Global variable to store the last action
last_action = {"type": None, "data": None}

# Update helper functions to use the DB_FILE
def read_todos(db_file: str = Depends(get_db_file)):
    try:
        with open(db_file, "r") as f:
            reader = csv.reader(f)
            return [{"id": row[0], "task": row[1], "done": row[2]} for row in reader if len(row) >= 3]
    except FileNotFoundError:
        return []
    except csv.Error:
        return []

def write_todos(todos, db_file: str = Depends(get_db_file)):
    with open(db_file, "w", newline="") as f:
        writer = csv.writer(f)
        for todo in todos:
            writer.writerow([todo["id"], todo["task"], todo["done"]])

def initialize_todos_file(db_file: str = Depends(get_db_file)):
    with open(db_file, "w", newline="") as f:
        pass

# Add this new function to update last_action
def update_last_action(action_type, data):
    global last_action
    last_action = {"type": action_type, "data": data}
    print(f"Last action updated: {last_action}")  # Debug log

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, todos: list = Depends(read_todos)):
    return templates.TemplateResponse(request, "index.html", {"todos": todos})

@app.post("/add")
async def add_todo(task: str = Form(...), done: bool = Form(False), db_file: str = Depends(get_db_file)):
    todos = read_todos(db_file)
    new_todo = {"id": str(uuid.uuid4()), "task": task, "done": str(done).lower()}
    todos.append(new_todo)
    write_todos(todos, db_file)
    update_last_action("add", new_todo)
    return RedirectResponse(url="/", status_code=303)

@app.post("/update/{todo_id}")
async def update_todo(todo_id: str, done: bool = Form(...), db_file: str = Depends(get_db_file)):
    todos = read_todos(db_file)
    todo = next((todo for todo in todos if todo["id"] == todo_id), None)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    old_todo = copy.deepcopy(todo)
    todo["done"] = str(done).lower()
    write_todos(todos, db_file)
    update_last_action("update", old_todo)
    return RedirectResponse(url="/", status_code=303)

@app.post("/delete/{todo_id}")
async def delete_todo(todo_id: str, db_file: str = Depends(get_db_file)):
    todos = read_todos(db_file)
    todo = next((todo for todo in todos if todo["id"] == todo_id), None)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    todos.remove(todo)
    write_todos(todos, db_file)
    update_last_action("delete", todo)
    return RedirectResponse(url="/", status_code=303)

@app.post("/clear")
async def clear_todos(db_file: str = Depends(get_db_file)):
    old_todos = read_todos(db_file)
    initialize_todos_file(db_file)
    update_last_action("clear", old_todos)
    return JSONResponse(content={"status": "success", "todos": []}, status_code=200)

@app.post("/undo")
async def undo_last_action(db_file: str = Depends(get_db_file)):
    global last_action
    todos = read_todos(db_file)
    
    print(f"Undo called. Last action: {last_action}")  # Debug log
    
    if last_action["type"] is None or last_action["data"] is None:
        print("No action to undo")  # Debug log
        return JSONResponse(content={"status": "no_action", "todos": todos}, status_code=200)
    
    if last_action["type"] == "add":
        print(f"Undoing add action: {last_action['data']}")  # Debug log
        todos = [todo for todo in todos if todo["id"] != last_action["data"]["id"]]
    elif last_action["type"] == "update":
        print(f"Undoing update action: {last_action['data']}")  # Debug log
        for todo in todos:
            if todo["id"] == last_action["data"]["id"]:
                todo.update(last_action["data"])
                break
    elif last_action["type"] == "delete":
        print(f"Undoing delete action: {last_action['data']}")  # Debug log
        todos.append(last_action["data"])
    elif last_action["type"] == "clear":
        print(f"Undoing clear action: {last_action['data']}")  # Debug log
        todos = last_action["data"]
    
    write_todos(todos, db_file)
    print(f"Todos after undo: {todos}")  # Debug log
    last_action = {"type": None, "data": None}
    return JSONResponse(content={"status": "success", "todos": todos}, status_code=200)

@app.get("/last-action")
async def get_last_action():
    return JSONResponse(content={"last_action": last_action}, status_code=200)

if __name__ == "__main__":
    import uvicorn
    initialize_todos_file()  # This will ensure an empty file at startup
    uvicorn.run(app, host="0.0.0.0", port=8000)
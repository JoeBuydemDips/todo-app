from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import csv
import uuid

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Helper functions for CSV operations
def read_todos():
    try:
        with open("todos.csv", "r") as f:
            reader = csv.reader(f)
            return [{"id": row[0], "task": row[1], "done": row[2]} for row in reader if len(row) >= 3]
    except FileNotFoundError:
        return []

def write_todos(todos):
    with open("todos.csv", "w", newline="") as f:
        writer = csv.writer(f)
        for todo in todos:
            writer.writerow([todo["id"], todo["task"], todo["done"]])

def initialize_todos_file():
    try:
        with open("todos.csv", "x") as f:
            pass  # Create the file if it doesn't exist
    except FileExistsError:
        pass  # File already exists, do nothing

@app.get("/")
async def home(request: Request):
    todos = read_todos()
    return templates.TemplateResponse("index.html", {"request": request, "todos": todos})

@app.post("/add")
async def add_todo(task: str = Form(...), done: bool = Form(False)):
    todos = read_todos()
    new_todo = {"id": str(uuid.uuid4()), "task": task, "done": done}
    todos.append(new_todo)
    write_todos(todos)
    return RedirectResponse(url="/", status_code=303)

@app.post("/update/{todo_id}")
async def update_todo(todo_id: str, done: bool = Form(...)):
    todos = read_todos()
    for todo in todos:
        if todo["id"] == todo_id:
            todo["done"] = done
            break
    write_todos(todos)
    return RedirectResponse(url="/", status_code=303)

@app.post("/delete/{todo_id}")
async def delete_todo(todo_id: str):
    todos = read_todos()
    todos = [todo for todo in todos if todo["id"] != todo_id]
    write_todos(todos)
    return RedirectResponse(url="/", status_code=303)

if __name__ == "__main__":
    import uvicorn
    initialize_todos_file()
    uvicorn.run(app, host="0.0.0.0", port=8000)
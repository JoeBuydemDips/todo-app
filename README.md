# FastAPI Todo App

A simple web-based todo application built with FastAPI and Jinja2 templates.
App was built with cursor IDE using Calude Sonnet 3.5 for code generation.

## Project Structure

```
todo-app/
├── static/
│   └── script.js
│   └── style.css
├── templates/
│   └── index.html
├── todos.csv
├── main.py
├── requirements.txt
```

## Setup

1. Clone the repository:

   ```
   git clone https://github.com/JoeBuydemDips/todo-app.git
   cd todo-app
   ```

2. Create a virtual environment:

   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```
   pip install fastapi uvicorn jinja2
   ```

## Running the App

1. Start the FastAPI server:

   ```
   python main.py
   ```

2. Open a web browser and navigate to:
   ```
   http://localhost:8000
   ```

## Features

- Add new todos
- Mark todos as complete/incomplete
- Delete todos
- Data persistence using CSV file

## Technologies Used

- Backend: Python, FastAPI
- Frontend: HTML, Jinja2 Templates
- Data Storage: CSV

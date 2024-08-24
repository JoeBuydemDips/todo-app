document.addEventListener('DOMContentLoaded', () => {
    const todoForm = document.getElementById('todo-form');
    const todoInput = document.getElementById('todo-input');
    const todoList = document.getElementById('todo-list');
    const darkModeToggle = document.getElementById('dark-mode-toggle');

    // Function to fetch and render todos
    const renderTodos = async () => {
        const response = await fetch('/');
        const html = await response.text();
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        const newTodoList = doc.getElementById('todo-list');
        
        todoList.innerHTML = newTodoList.innerHTML;
        
        // Add 'new-item' class to the last item for animation
        if (todoList.lastElementChild) {
            todoList.lastElementChild.classList.add('new-item');
            setTimeout(() => todoList.lastElementChild.classList.remove('new-item'), 500);
        }
    };

    // Function to update todo status
    const updateTodoStatus = async (id, done) => {
        await fetch(`/update/${id}`, {
            method: 'POST',
            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
            body: `done=${done}`
        });
    };

    // Add new todo
    todoForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const task = todoInput.value.trim();
        if (task) {
            await fetch('/add', {
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                body: `task=${encodeURIComponent(task)}&done=false`
            });
            todoInput.value = '';
            renderTodos();
        }
    });

    // Delete todo
    todoList.addEventListener('click', async (e) => {
        if (e.target.classList.contains('delete-btn')) {
            const todoItem = e.target.closest('li');
            const todoId = e.target.dataset.id;
            
            todoItem.classList.add('deleting');
            
            await fetch(`/delete/${todoId}`, {method: 'POST'});
            
            setTimeout(() => {
                todoItem.remove();
            }, 500);
        }
    });

    // Handle checkbox changes
    todoList.addEventListener('change', async (e) => {
        if (e.target.classList.contains('todo-checkbox')) {
            const todoItem = e.target.closest('li');
            const todoId = todoItem.dataset.id;
            const isDone = e.target.checked;
            
            todoItem.classList.toggle('done', isDone);
            await updateTodoStatus(todoId, isDone);
        }
    });

    // Dark mode toggle
    darkModeToggle.addEventListener('click', () => {
        document.body.classList.toggle('dark-mode');
        darkModeToggle.textContent = document.body.classList.contains('dark-mode') ? '☀️' : '🌙';
        localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
    });

    // Check for saved dark mode preference
    if (localStorage.getItem('darkMode') === 'true') {
        document.body.classList.add('dark-mode');
        darkModeToggle.textContent = '☀️';
    }

    // Initial render
    renderTodos();

    // Add event listener for todo checkboxes
    document.querySelectorAll('.todo-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', (event) => {
            const listItem = event.target.closest('li');
            if (event.target.checked) {
                listItem.classList.add('done');
            } else {
                listItem.classList.remove('done');
            }
        });
    });
});
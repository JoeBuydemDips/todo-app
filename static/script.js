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

    // Add new todo
    todoForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const task = todoInput.value.trim();
        if (task) {
            await fetch('/add', {
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                body: `task=${encodeURIComponent(task)}`
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
});
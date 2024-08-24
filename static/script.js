document.addEventListener('DOMContentLoaded', () => {
    const todoForm = document.getElementById('todo-form');
    const todoInput = document.getElementById('todo-input');
    const todoList = document.getElementById('todo-list');
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    const clearTodosButton = document.getElementById('clear-todos');
    const undoButton = document.getElementById('undo-button');

    // Function to fetch and render todos
    const renderTodos = async (animateLastItem = false) => {
        const response = await fetch('/');
        const html = await response.text();
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        const newTodoList = doc.getElementById('todo-list');
        
        if (newTodoList && newTodoList.children.length > 0) {
            // Create a document fragment to build the new list
            const fragment = document.createDocumentFragment();
            Array.from(newTodoList.children).forEach(newItem => {
                const existingItem = todoList.querySelector(`[data-id="${newItem.dataset.id}"]`);
                if (existingItem) {
                    // Update existing item
                    existingItem.innerHTML = newItem.innerHTML;
                    // Update checkbox state and 'done' class
                    const checkbox = existingItem.querySelector('.todo-checkbox');
                    if (checkbox) {
                        checkbox.checked = newItem.querySelector('.todo-checkbox').checked;
                        existingItem.classList.toggle('done', checkbox.checked);
                    }
                    fragment.appendChild(existingItem);
                } else {
                    // Add new item
                    const newItemClone = newItem.cloneNode(true);
                    // Set 'done' class based on checkbox state
                    const checkbox = newItemClone.querySelector('.todo-checkbox');
                    if (checkbox) {
                        newItemClone.classList.toggle('done', checkbox.checked);
                    }
                    fragment.appendChild(newItemClone);
                }
            });
            
            // Replace the entire list content
            todoList.innerHTML = '';
            todoList.appendChild(fragment);
            
            // Animate the last item if specified
            if (animateLastItem && todoList.lastElementChild) {
                todoList.lastElementChild.classList.add('new-item');
                setTimeout(() => todoList.lastElementChild.classList.remove('new-item'), 500);
            }
        } else {
            todoList.innerHTML = '<li>No todos yet. Add a new one!</li>';
        }
        
        // Reattach event listeners for checkboxes
        attachCheckboxListeners();
    };

    // Function to attach event listeners to checkboxes
    const attachCheckboxListeners = () => {
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
            renderTodos(true); // Animate the last item when adding a new todo
            await updateUndoButtonState();
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
            await updateUndoButtonState();
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
            await updateUndoButtonState();
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

    // Clear all todos
    clearTodosButton.addEventListener('click', async () => {
        try {
            const response = await fetch('/clear', { method: 'POST' });
            if (response.ok) {
                const result = await response.json();
                if (result.status === 'success') {
                    console.log('Todos cleared successfully');
                    todoList.innerHTML = ''; // Clear the list in the DOM
                    await renderTodos(); // Re-render the todo list from the server
                    await updateUndoButtonState();
                } else {
                    console.error('Failed to clear todos');
                }
            } else {
                console.error('Failed to clear todos');
            }
        } catch (error) {
            console.error('Error clearing todos:', error);
        }
    });

    // Undo last action
    undoButton.addEventListener('click', async () => {
        console.log('Undo button clicked');
        try {
            const response = await fetch('/undo', { method: 'POST' });
            console.log('Undo response status:', response.status);
            if (response.ok) {
                const result = await response.json();
                console.log('Undo response:', result);
                if (result.status === 'no_action') {
                    console.log('No action to undo');
                    undoButton.disabled = true;
                } else if (result.status === 'success') {
                    console.log('Last action undone successfully');
                    console.log('Updated todos:', result.todos);
                    await renderTodos(false); // Re-render todos without animation
                    undoButton.disabled = false; // Enable the button after a successful undo
                } else {
                    console.error('Failed to undo last action');
                }
            } else {
                console.error('Failed to undo last action, status:', response.status);
            }
        } catch (error) {
            console.error('Error undoing last action:', error);
        }
    });

    // Add this function to check if there are actions to undo
    async function checkUndoAvailability() {
        try {
            const response = await fetch('/last-action');
            if (response.ok) {
                const result = await response.json();
                undoButton.disabled = result.last_action.type === null;
            }
        } catch (error) {
            console.error('Error checking undo availability:', error);
        }
    }

    // Call this function after each action that modifies the todo list
    async function updateUndoButtonState() {
        await checkUndoAvailability();
    }

    // Call this function on initial load
    document.addEventListener('DOMContentLoaded', async () => {
        // ... (rest of the code)
        await updateUndoButtonState();
    });

    // Helper function to create a todo list item
    function createTodoElement(todo) {
        const li = document.createElement('li');
        li.dataset.id = todo.id;
        li.innerHTML = `
            <input type="checkbox" class="todo-checkbox" ${todo.done === 'true' ? 'checked' : ''}>
            <span>${todo.task}</span>
            <button class="delete-btn" data-id="${todo.id}">Delete</button>
        `;
        li.classList.toggle('done', todo.done === 'true');
        return li;
    }

    // Initial render
    renderTodos(false); // Don't animate on initial render

    // Add event listener for todo checkboxes
    attachCheckboxListeners();
});
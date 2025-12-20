const todoInput = document.getElementById('new-todo');
const addBtn = document.getElementById('add-btn');
const todoList = document.getElementById('todo-list');

async function loadTodos() {
    const res = await fetch('/api/todos');
    const todos = await res.json();
    todoList.innerHTML = '';
    todos.forEach(renderTodo);
}

function renderTodo(todo) {
    const li = document.createElement('li');
    li.className = 'todo-item' + (todo.completed ? ' completed' : '');
    li.dataset.id = todo.id;

    li.innerHTML = `
        <input type="checkbox" ${todo.completed ? 'checked' : ''}>
        <span>${todo.title}</span>
        <button class="delete-btn">Удалить</button>
    `;

    li.querySelector('input[type="checkbox"]').addEventListener('change', async (e) => {
        await fetch(`/api/todos/${todo.id}/toggle`, { method: 'PUT' });
        loadTodos();
    });

    li.querySelector('.delete-btn').addEventListener('click', async () => {
        await fetch(`/api/todos/${todo.id}`, { method: 'DELETE' });
        loadTodos();
    });

    todoList.appendChild(li);
}

async function addTodo() {
    const title = todoInput.value.trim();
    if (!title) return;

    await fetch('/api/todos', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title })
    });

    todoInput.value = '';
    loadTodos();
}

addBtn.addEventListener('click', addTodo);
todoInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') addTodo();
});


loadTodos();

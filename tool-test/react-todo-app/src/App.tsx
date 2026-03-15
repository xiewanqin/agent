import { useState, useEffect, useCallback } from 'react';
import './App.css';

interface Todo {
  id: string;
  text: string;
  completed: boolean;
  createdAt: Date;
}

function App() {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [newTodo, setNewTodo] = useState('');
  const [filter, setFilter] = useState<'all' | 'active' | 'completed'>('all');
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editText, setEditText] = useState('');
  const [isAdding, setIsAdding] = useState(false);

  // Load todos from localStorage on mount
  useEffect(() => {
    const savedTodos = localStorage.getItem('todos');
    if (savedTodos) {
      try {
        const parsed = JSON.parse(savedTodos);
        // Convert string dates back to Date objects
        const todosWithDates = parsed.map((todo: any) => ({
          ...todo,
          createdAt: new Date(todo.createdAt)
        }));
        setTodos(todosWithDates);
      } catch (e) {
        console.error('Failed to parse todos from localStorage', e);
      }
    }
  }, []);

  // Save todos to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem('todos', JSON.stringify(todos));
  }, [todos]);

  const addTodo = useCallback(() => {
    if (newTodo.trim() === '') return;
    
    const newTodoItem: Todo = {
      id: Date.now().toString(),
      text: newTodo.trim(),
      completed: false,
      createdAt: new Date()
    };
    
    setTodos(prev => [newTodoItem, ...prev]);
    setNewTodo('');
    setIsAdding(false);
  }, [newTodo]);

  const toggleTodo = useCallback((id: string) => {
    setTodos(prev => 
      prev.map(todo => 
        todo.id === id ? { ...todo, completed: !todo.completed } : todo
      )
    );
  }, []);

  const deleteTodo = useCallback((id: string) => {
    setTodos(prev => prev.filter(todo => todo.id !== id));
    if (editingId === id) {
      setEditingId(null);
    }
  }, [editingId]);

  const startEditing = useCallback((todo: Todo) => {
    setEditingId(todo.id);
    setEditText(todo.text);
  }, []);

  const saveEdit = useCallback(() => {
    if (editingId && editText.trim() !== '') {
      setTodos(prev => 
        prev.map(todo => 
          todo.id === editingId ? { ...todo, text: editText.trim() } : todo
        )
      );
      setEditingId(null);
      setEditText('');
    }
  }, [editingId, editText]);

  const cancelEdit = useCallback(() => {
    setEditingId(null);
    setEditText('');
  }, []);

  const clearCompleted = useCallback(() => {
    setTodos(prev => prev.filter(todo => !todo.completed));
  }, []);

  // Filter todos based on current filter
  const filteredTodos = todos.filter(todo => {
    if (filter === 'active') return !todo.completed;
    if (filter === 'completed') return todo.completed;
    return true;
  });

  const activeCount = todos.filter(todo => !todo.completed).length;
  const completedCount = todos.length - activeCount;

  // Handle Enter key for adding and editing
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      if (editingId) {
        saveEdit();
      } else {
        addTodo();
      }
    }
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1 className="app-title">✨ TodoList Pro</h1>
        <p className="app-subtitle">Organize your life with style</p>
      </header>

      <main className="app-main">
        {/* Add Todo Form */}
        <div className="add-todo-section">
          <div className="input-group">
            <input
              type="text"
              value={newTodo}
              onChange={(e) => setNewTodo(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="What needs to be done?"
              className="todo-input"
              autoFocus
            />
            <button 
              onClick={addTodo}
              disabled={!newTodo.trim()}
              className="add-btn"
            >
              ➕
            </button>
          </div>
        </div>

        {/* Stats Bar */}
        <div className="stats-bar">
          <span className="stats-text">
            {activeCount} {activeCount === 1 ? 'task' : 'tasks'} left
          </span>
          <button 
            onClick={clearCompleted}
            disabled={completedCount === 0}
            className="clear-btn"
          >
            Clear completed
          </button>
        </div>

        {/* Todo List */}
        <div className="todo-list-container">
          {filteredTodos.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">📝</div>
              <h3 className="empty-title">
                {filter === 'all' 
                  ? 'No tasks yet' 
                  : filter === 'active' 
                    ? 'All tasks completed!' 
                    : 'No completed tasks'}
              </h3>
              <p className="empty-text">
                {filter === 'all' 
                  ? 'Add your first task to get started' 
                  : filter === 'active' 
                    ? 'Great job! You\'ve completed all tasks.' 
                    : 'Complete some tasks to see them here.'}
              </p>
            </div>
          ) : (
            <ul className="todo-list">
              {filteredTodos.map((todo) => (
                <li 
                  key={todo.id} 
                  className={`todo-item ${todo.completed ? 'completed' : ''} ${editingId === todo.id ? 'editing' : ''}`}
                >
                  <div className="todo-content">
                    <input
                      type="checkbox"
                      checked={todo.completed}
                      onChange={() => toggleTodo(todo.id)}
                      className="todo-checkbox"
                    />
                    {editingId === todo.id ? (
                      <div className="edit-form">
                        <input
                          type="text"
                          value={editText}
                          onChange={(e) => setEditText(e.target.value)}
                          onKeyDown={handleKeyDown}
                          className="edit-input"
                          autoFocus
                        />
                        <div className="edit-actions">
                          <button 
                            onClick={saveEdit}
                            className="save-btn"
                            aria-label="Save edit"
                          >
                            ✅
                          </button>
                          <button 
                            onClick={cancelEdit}
                            className="cancel-btn"
                            aria-label="Cancel edit"
                          >
                            ❌
                          </button>
                        </div>
                      </div>
                    ) : (
                      <div className="todo-text">
                        <span className={todo.completed ? 'completed-text' : ''}>
                          {todo.text}
                        </span>
                        <div className="todo-meta">
                          <span className="todo-date">
                            {todo.createdAt.toLocaleDateString('en-US', { 
                              month: 'short', 
                              day: 'numeric',
                              hour: '2-digit',
                              minute: '2-digit' 
                            })}
                          </span>
                        </div>
                      </div>
                    )}
                  </div>
                  {editingId !== todo.id && (
                    <div className="todo-actions">
                      <button 
                        onClick={() => startEditing(todo)}
                        className="edit-btn"
                        aria-label="Edit task"
                      >
                        ✏️
                      </button>
                      <button 
                        onClick={() => deleteTodo(todo.id)}
                        className="delete-btn"
                        aria-label="Delete task"
                      >
                        🗑️
                      </button>
                    </div>
                  )}
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Filter Controls */}
        <div className="filter-controls">
          <button 
            onClick={() => setFilter('all')}
            className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
          >
            All
          </button>
          <button 
            onClick={() => setFilter('active')}
            className={`filter-btn ${filter === 'active' ? 'active' : ''}`}
          >
            Active
          </button>
          <button 
            onClick={() => setFilter('completed')}
            className={`filter-btn ${filter === 'completed' ? 'active' : ''}`}
          >
            Completed
          </button>
        </div>
      </main>

      <footer className="app-footer">
        <p>© {new Date().getFullYear()} TodoList Pro • Built with React & Vite</p>
      </footer>
    </div>
  );
}

export default App;

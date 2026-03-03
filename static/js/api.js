const API_BASE = 'http://127.0.0.1:8000';

// Функция экранирования HTML (защита от XSS)
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Функция санитизации ввода (удаляет HTML-теги)
function sanitizeInput(text) {
    if (!text) return '';
    // Удаляем все HTML-теги
    return text.replace(/<[^>]*>/g, '')
               .replace(/javascript:/gi, '')
               .replace(/vbscript:/gi, '')
               .replace(/on\w+\s*=/gi, '');
}

class API {
    getToken() { return localStorage.getItem('access_token'); }
    setToken(token) { localStorage.setItem('access_token', token); }
    removeToken() { localStorage.removeItem('access_token'); }
    isAuthenticated() { return !!this.getToken(); }
    
    getUserFromToken() {
        const token = this.getToken();
        if (!token) return null;
        try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            return { user_id: payload.user_id, username: payload.username };
        } catch (e) { return null; }
    }

    async login(username, password) {
        const response = await fetch(`${API_BASE}/api/token/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Ошибка входа');
        }
        const data = await response.json();
        this.setToken(data.access);
        return data;
    }

    logout() { this.removeToken(); }

    async getBooks() {
        const response = await fetch(`${API_BASE}/books/`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${this.getToken()}`,
                'Content-Type': 'application/json',
            }
        });
        if (!response.ok) {
            if (response.status === 401) { this.logout(); throw new Error('Сессия истекла'); }
            throw new Error('Ошибка загрузки книг');
        }
        return await response.json();
    }

    async createBook(title, author) {
        // Санитизация перед отправкой
        const cleanTitle = sanitizeInput(title);
        const cleanAuthor = sanitizeInput(author);
        
        const response = await fetch(`${API_BASE}/books/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.getToken()}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ title: cleanTitle, author: cleanAuthor })
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.title?.[0] || error.author?.[0] || 'Ошибка создания');
        }
        return await response.json();
    }

    async updateBook(id, title, author) {
        // Санитизация перед отправкой
        const cleanTitle = sanitizeInput(title);
        const cleanAuthor = sanitizeInput(author);
        
        const response = await fetch(`${API_BASE}/books/${id}/`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${this.getToken()}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ title: cleanTitle, author: cleanAuthor })
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.title?.[0] || error.author?.[0] || 'Ошибка обновления');
        }
        return await response.json();
    }

    async deleteBook(id) {
        const response = await fetch(`${API_BASE}/books/${id}/`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${this.getToken()}` }
        });
        if (!response.ok) throw new Error('Ошибка удаления');
        return true;
    }
}

const api = new API();
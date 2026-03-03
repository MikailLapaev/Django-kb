document.addEventListener('DOMContentLoaded', () => { initApp(); });

function initApp() {
    if (api.isAuthenticated()) {
        const user = api.getUserFromToken();
        if (user) showUserInfo(user);
        else { api.logout(); redirectToLogin(); }
    } else {
        if (!window.location.pathname.includes('login')) redirectToLogin();
    }

    const loginForm = document.getElementById('login-form');
    if (loginForm) initLoginPage();

    const booksList = document.getElementById('books-list');
    if (booksList) initBooksPage();
}

function showUserInfo(user) {
    const userInfo = document.getElementById('user-info');
    const logoutBtn = document.getElementById('logout-btn');
    if (userInfo) { 
        userInfo.textContent = `👤 ${escapeHtml(user.username)}`;
        userInfo.style.display = 'block'; 
    }
    if (logoutBtn) {
        logoutBtn.style.display = 'block';
        logoutBtn.addEventListener('click', () => { api.logout(); window.location.href = '/login/'; });
    }
}

function redirectToLogin() {
    if (!window.location.pathname.includes('login')) window.location.href = '/login/';
}

function initLoginPage() {
    const loginForm = document.getElementById('login-form');
    const errorMessage = document.getElementById('error-message');
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        try {
            await api.login(username, password);
            window.location.href = '/books-page/';
        } catch (error) {
            errorMessage.textContent = escapeHtml(error.message);
            errorMessage.style.display = 'block';
        }
    });
    if (api.isAuthenticated()) window.location.href = '/books-page/';
}

function initBooksPage() {
    loadBooks();
    initAddBookForm();
    initEditBookForm();
}

async function loadBooks() {
    const booksList = document.getElementById('books-list');
    const noBooks = document.getElementById('no-books');
    try {
        const books = await api.getBooks();
        booksList.innerHTML = '';
        if (books.length === 0) {
            booksList.style.display = 'none';
            noBooks.style.display = 'block';
            return;
        }
        booksList.style.display = 'grid';
        noBooks.style.display = 'none';
        books.forEach(book => booksList.appendChild(createBookCard(book)));
    } catch (error) {
        booksList.innerHTML = `<div class="error-message" style="display:block">${escapeHtml(error.message)}</div>`;
    }
}

// Безопасное создание карточки книги
function createBookCard(book) {
    const card = document.createElement('div');
    card.className = 'book-card';
    

    const titleEl = document.createElement('h3');
    titleEl.textContent = `📖 ${book.title}`; 
    
    const authorLabel = document.createElement('strong');
    authorLabel.textContent = 'Автор:';
    
    const authorEl = document.createElement('p');
    authorEl.appendChild(authorLabel);
    authorEl.appendChild(document.createTextNode(` ${book.author}`));  // ✅ Безопасно
    
    const ownerEl = document.createElement('p');
    ownerEl.className = 'owner';
    ownerEl.textContent = `👤 Владелец: ${book.owner}`;  // ✅ Безопасно
    
    const actionsEl = document.createElement('div');
    actionsEl.className = 'book-actions';
    
    const editBtn = document.createElement('button');
    editBtn.className = 'btn btn-secondary';
    editBtn.textContent = '✏️ Редактировать';
    editBtn.onclick = () => openEditForm(book.id, book.title, book.author);
    
    const deleteBtn = document.createElement('button');
    deleteBtn.className = 'btn btn-danger';
    deleteBtn.textContent = '🗑️ Удалить';
    deleteBtn.onclick = () => deleteBook(book.id);
    
    actionsEl.appendChild(editBtn);
    actionsEl.appendChild(deleteBtn);
    
    card.appendChild(titleEl);
    card.appendChild(authorEl);
    card.appendChild(ownerEl);
    card.appendChild(actionsEl);
    
    return card;
}

function initAddBookForm() {
    const addBtn = document.getElementById('add-book-btn');
    const formContainer = document.getElementById('add-book-form');
    const cancelBtn = document.getElementById('cancel-btn');
    const bookForm = document.getElementById('book-form');
    const formError = document.getElementById('form-error');

    addBtn.addEventListener('click', () => { 
        formContainer.style.display = 'block'; 
        addBtn.style.display = 'none'; 
    });
    
    cancelBtn.addEventListener('click', () => {
        formContainer.style.display = 'none';
        addBtn.style.display = 'block';
        bookForm.reset();
        formError.style.display = 'none';
    });

    bookForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const title = document.getElementById('title').value;
        const author = document.getElementById('author').value;
        try {
            await api.createBook(title, author);
            bookForm.reset();
            formContainer.style.display = 'none';
            addBtn.style.display = 'block';
            loadBooks();
        } catch (error) {
            formError.textContent = escapeHtml(error.message);
            formError.style.display = 'block';
        }
    });
}

function openEditForm(id, title, author) {
    const editFormContainer = document.getElementById('edit-book-form');
    const addBtn = document.getElementById('add-book-btn');
    
    document.getElementById('edit-book-id').value = id;
    document.getElementById('edit-title').value = title;
    document.getElementById('edit-author').value = author;
    
    editFormContainer.style.display = 'block';
    addBtn.style.display = 'none';
    
    document.getElementById('add-book-form').style.display = 'none';
    document.getElementById('form-error').style.display = 'none';
}

function initEditBookForm() {
    const editFormContainer = document.getElementById('edit-book-form');
    const cancelEditBtn = document.getElementById('cancel-edit-btn');
    const editForm = document.getElementById('edit-form');
    const editFormError = document.getElementById('edit-form-error');
    const addBtn = document.getElementById('add-book-btn');

    cancelEditBtn.addEventListener('click', () => {
        editFormContainer.style.display = 'none';
        addBtn.style.display = 'block';
        editForm.reset();
        editFormError.style.display = 'none';
    });

    editForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const id = document.getElementById('edit-book-id').value;
        const title = document.getElementById('edit-title').value;
        const author = document.getElementById('edit-author').value;

        try {
            await api.updateBook(id, title, author);
            
            editFormContainer.style.display = 'none';
            addBtn.style.display = 'block';
            editForm.reset();
            editFormError.style.display = 'none';
            loadBooks();
        } catch (error) {
            editFormError.textContent = escapeHtml(error.message);
            editFormError.style.display = 'block';
        }
    });
}

async function deleteBook(id) {
    if (!confirm('Вы уверены, что хотите удалить эту книгу?')) return;
    try { 
        await api.deleteBook(id); 
        loadBooks(); 
    } catch (error) { 
        alert(error.message); 
    }
}
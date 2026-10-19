function getCsrfToken() {
    const metaToken = document.querySelector('[name=csrfmiddlewaretoken]');
    if (metaToken) return metaToken.value;
    const match = document.cookie.match(/csrftoken=([^;]+)/);
    return match ? match[1] : '';
}

async function apiRequest(url, options = {}) {
    const defaultHeaders = {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken(),
    };
    const response = await fetch(url, {
        ...options,
        headers: {
            ...defaultHeaders,
            ...(options.headers || {})
        },
        credentials: 'same-origin'
    });

    let data = null;
    if (response.status !== 204) {
        data = await response.json().catch(() => null);
    }

    if (!response.ok) {
        let errorMsg = 'Произошла ошибка при выполнении операции.';
        if (data) {
            if (typeof data === 'object') {
                errorMsg = Object.entries(data)
                    .map(([field, errs]) => `${field !== 'detail' ? field + ': ' : ''}${Array.isArray(errs) ? errs.join(', ') : errs}`)
                    .join(' | ');
            } else {
                errorMsg = String(data);
            }
        }
        throw new Error(errorMsg);
    }
    return data;
}

function showAlert(message, type = 'success') {
    const container = document.getElementById('alert-container');
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        <div class="d-flex">
            <div>${message}</div>
        </div>
        <a class="btn-close" data-bs-dismiss="alert" aria-label="close"></a>
    `;
    container.replaceChildren(alert);
    setTimeout(() => {
        alert.classList.remove('show');
        setTimeout(() => alert.remove(), 150);
    }, 4500);
}

let allCategories = [];
let allTickets = [];
let ticketToDeleteId = null;

// Загрузка категорий с сервера
async function loadCategories() {
    try {
        allCategories = await apiRequest('/api/categories/');
        
        // Селект в модалке создания
        const modalSelect = document.getElementById('ticket-category');
        modalSelect.replaceChildren();
        
        // Селект в панели фильтрации
        const filterSelect = document.getElementById('category-filter');
        filterSelect.innerHTML = '<option value="">Все категории МАИ</option>';

        allCategories.forEach(cat => {
            const optModal = document.createElement('option');
            optModal.value = cat.id;
            optModal.textContent = `${cat.name} (${cat.code || 'МАИ'})`;
            modalSelect.appendChild(optModal);

            const optFilter = document.createElement('option');
            optFilter.value = cat.id;
            optFilter.textContent = `${cat.name}`;
            filterSelect.appendChild(optFilter);
        });
    } catch (err) {
        showAlert('Ошибка загрузки справочника категорий: ' + err.message, 'danger');
    }
}

// Загрузка обращений
async function loadTickets() {
    const loading = document.getElementById('loading');
    const statusFilter = document.getElementById('status-filter').value;
    
    loading.hidden = false;
    const url = '/api/tickets/' + (statusFilter ? `?status=${statusFilter}` : '');

    try {
        allTickets = await apiRequest(url);
        applyClientFilters();
    } catch (err) {
        showAlert('Не удалось получить список обращений: ' + err.message, 'danger');
    } finally {
        loading.hidden = true;
    }
}

// Клиентская мульти-фильтрация (Поиск + Категория + Статус)
function applyClientFilters() {
    const query = document.getElementById('live-search').value.toLowerCase().trim();
    const categoryId = document.getElementById('category-filter').value;

    let filtered = allTickets;

    if (categoryId) {
        filtered = filtered.filter(t => String(t.category) === String(categoryId));
    }

    if (query) {
        filtered = filtered.filter(t => 
            t.title.toLowerCase().includes(query) || 
            (t.description && t.description.toLowerCase().includes(query)) ||
            t.category_name.toLowerCase().includes(query)
        );
    }

    renderTicketsTable(filtered);
    updateKPI(filtered);
}

// Рендеринг таблицы
function renderTicketsTable(tickets) {
    const tbody = document.getElementById('tickets-tbody');
    tbody.replaceChildren();

    if (tickets.length === 0) {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td colspan="7" class="text-center text-muted py-4">По заданным критериям ничего не найдено</td>`;
        tbody.appendChild(tr);
        return;
    }

    tickets.forEach(ticket => {
        const tr = document.createElement('tr');
        
        let statusBadge = '<span class="badge bg-primary-lt">Новая</span>';
        if (ticket.status === 'progress') statusBadge = '<span class="badge bg-warning-lt">В работе</span>';
        if (ticket.status === 'done') statusBadge = '<span class="badge bg-success-lt">Выполнена</span>';

        let priorityBadge = '<span class="badge bg-secondary-lt">Обычный</span>';
        if (ticket.priority === 'low') priorityBadge = '<span class="badge bg-info-lt">Низкий</span>';
        if (ticket.priority === 'high') priorityBadge = '<span class="badge bg-danger-lt">Срочный</span>';

        let actionButtons = '';
        if (ticket.status === 'new') {
            actionButtons += `<button class="btn btn-sm btn-outline-warning me-1" onclick="changeStatus(${ticket.id}, 'progress')">В работу</button>`;
            actionButtons += `<button class="btn btn-sm btn-outline-secondary me-1" title="Тест блокировки бизнес-правила" onclick="changeStatus(${ticket.id}, 'done')">В выполненные (тест)</button>`;
        } else if (ticket.status === 'progress') {
            actionButtons += `<button class="btn btn-sm btn-outline-success me-1" onclick="changeStatus(${ticket.id}, 'done')">Завершить</button>`;
        }

        actionButtons += `<button class="btn btn-sm btn-outline-danger" onclick="openDeleteModal(${ticket.id}, '${ticket.title.replace(/'/g, "\\'")}')">Удалить</button>`;

        const dateStr = new Date(ticket.created_at).toLocaleString('ru-RU', {
            day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit'
        });

        tr.innerHTML = `
            <td><span class="text-muted">#${ticket.id}</span></td>
            <td><strong>${ticket.title}</strong><div class="text-muted small">${ticket.description || 'Без описания'}</div></td>
            <td>${ticket.category_name}</td>
            <td>${priorityBadge}</td>
            <td>${statusBadge}</td>
            <td>${dateStr}</td>
            <td><div class="btn-list flex-nowrap">${actionButtons}</div></td>
        `;
        tbody.appendChild(tr);
    });
}

function updateKPI(tickets) {
    document.getElementById('kpi-total').textContent = tickets.length;
    document.getElementById('kpi-new').textContent = tickets.filter(t => t.status === 'new').length;
    document.getElementById('kpi-progress').textContent = tickets.filter(t => t.status === 'progress').length;
    document.getElementById('kpi-done').textContent = tickets.filter(t => t.status === 'done').length;
}

async function changeStatus(ticketId, newStatus) {
    try {
        await apiRequest(`/api/tickets/${ticketId}/`, {
            method: 'PATCH',
            body: JSON.stringify({ status: newStatus })
        });
        showAlert('Статус обращения успешно обновлен!', 'success');
        await loadTickets();
    } catch (err) {
        showAlert('Ошибка изменения статуса: ' + err.message, 'danger');
    }
}

function openDeleteModal(ticketId, title) {
    ticketToDeleteId = ticketId;
    document.getElementById('delete-ticket-name').textContent = `«${title}»`;
    const deleteModal = new bootstrap.Modal(document.getElementById('modal-delete'));
    deleteModal.show();
}

document.getElementById('confirm-delete-btn').addEventListener('click', async () => {
    if (!ticketToDeleteId) return;
    try {
        await apiRequest(`/api/tickets/${ticketToDeleteId}/`, { method: 'DELETE' });
        const modalEl = document.getElementById('modal-delete');
        const modal = bootstrap.Modal.getInstance(modalEl);
        if (modal) modal.hide();
        showAlert('Обращение успешно удалено из базы данных', 'info');
        await loadTickets();
    } catch (err) {
        showAlert('Ошибка удаления: ' + err.message, 'danger');
    } finally {
        ticketToDeleteId = null;
    }
});

document.getElementById('create-ticket-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const modalError = document.getElementById('modal-error');
    modalError.style.display = 'none';

    const payload = {
        title: document.getElementById('ticket-title').value,
        category: Number(document.getElementById('ticket-category').value),
        priority: document.getElementById('ticket-priority').value,
        description: document.getElementById('ticket-desc').value,
        status: 'new'
    };

    try {
        await apiRequest('/api/tickets/', {
            method: 'POST',
            body: JSON.stringify(payload)
        });

        e.target.reset();
        const modalEl = document.getElementById('modal-create-ticket');
        const modal = bootstrap.Modal.getInstance(modalEl);
        if (modal) modal.hide();

        showAlert('Обращение успешно зарегистрировано через REST API!', 'success');
        await loadTickets();
    } catch (err) {
        modalError.textContent = err.message;
        modalError.style.display = 'block';
    }
});

// Экспорт текущей выборки в CSV файл
document.getElementById('btn-export-csv').addEventListener('click', () => {
    if (!allTickets || allTickets.length === 0) {
        showAlert('Нет данных для выгрузки в CSV', 'warning');
        return;
    }
    const headers = ['ID', 'Тема', 'Категория', 'Приоритет', 'Статус', 'Дата создания'];
    const rows = allTickets.map(t => [
        t.id,
        `"${t.title.replace(/"/g, '""')}"`,
        `"${t.category_name.replace(/"/g, '""')}"`,
        t.priority,
        t.status,
        t.created_at
    ]);

    const csvContent = '\uFEFF' + [headers.join(';'), ...rows.map(e => e.join(';'))].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `appeals_export_${new Date().toISOString().slice(0,10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    showAlert('Реестр успешно экспортирован в CSV!', 'success');
});

// Слушатели событий
document.getElementById('status-filter').addEventListener('change', loadTickets);
document.getElementById('category-filter').addEventListener('change', applyClientFilters);
document.getElementById('live-search').addEventListener('input', applyClientFilters);

document.addEventListener('DOMContentLoaded', () => {
    loadCategories();
    loadTickets();
});
const API_BASE_URL = 'http://localhost:8080';
let isDeletingTask = false;


$(function () {
    const $taskLists = $('#activeTasksList, #doneTasksList');
    loadCurrentUser();

    $('#registerForm').on('submit', function (event) {
        event.preventDefault();
        register();
    });

    $('#loginForm').on('submit', function (event) {
        event.preventDefault();
        login();
    });

    $('#logoutButton').on('click', function () {
        logout();
    });

    $('#addTaskButton').on('click', function () {
        addTask();
    });

    $('#newTaskTitleInput').on('keydown', function (event) {
        if (event.key === 'Enter') {
            addTask();
        }
    });

    $taskLists.on('change', '.form-check-input', function () {
        const task = $(this).closest('li').data('task');
        toggleTask(task.id, $(this).prop('checked'));
    });

    $taskLists.on('click', '.task-title', function () {
        const task = $(this).closest('li').data('task');
        openTaskModal(task);
    });

    $('#taskModal').on('hidden.bs.modal', function () {
        if (isDeletingTask) {
            isDeletingTask = false;
            return;
        }
        saveTaskFromModal();
    });

    $('#deleteTaskButton').on('click', function () {
        isDeletingTask = true;
        deleteTask($('#taskIdInput').val());
        bootstrap.Modal.getOrCreateInstance($('#taskModal')[0]).hide();
    });

});

function loadCurrentUser() {
    apiRequest({
        url: API_BASE_URL + '/user',
        method: 'GET',
        xhrFields: {
            withCredentials: true
        }
    })
        .done(function (user) {
            showAuthorizedState(user);
        })
        .fail(function () {
            showGuestState();
        });
}

function showAuthorizedState(user) {
    $('#userEmailLabel').text(user.email);
    $('#guestArea').addClass('d-none');
    $('#userArea').removeClass('d-none');
    $('#mainContent').removeClass('d-none');
    loadTasks();
}

function showGuestState() {
    $('#userEmailLabel').text('');
    $('#userArea').addClass('d-none');
    $('#guestArea').removeClass('d-none');
    $('#mainContent').addClass('d-none');
    $('#activeTasksList').empty();
    $('#doneTasksList').empty();
}

function register() {
    const email = $('#registerEmailInput').val();
    const password = $('#registerPasswordInput').val();
    const passwordRepeat = $('#registerPasswordRepeatInput').val();

    if (password !== passwordRepeat) {
        showFormError('#registerError', 'Пароли не совпадают');
        return;
    }

    hideFormError('#registerError');

    $.ajax({
        url: API_BASE_URL + '/user',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({email: email, password: password, password_repeat: passwordRepeat}),
        xhrFields: {
            withCredentials: true
        }
    })
        .done(function (user) {
            $('#registerForm')[0].reset();
            bootstrap.Modal.getInstance($('#registerModal')[0]).hide();
            showAuthorizedState(user);
        })
        .fail(function (jqXHR) {
            showFormError('#registerError', getRegisterErrorMessage(jqXHR.status));
        });
}

function showFormError(selector, message) {
    $(selector).text(message).removeClass('d-none');
}

function hideFormError(selector) {
    $(selector).text('').addClass('d-none');
}

function getRegisterErrorMessage(status) {
    if (status === 409) {
        return 'Пользователь с таким email уже зарегистрирован';
    }
    if (status === 422) {
        return 'Проверьте правильность заполнения полей';
    }
    return 'Что-то пошло не так, попробуйте позже';
}

function login() {
    const email = $('#loginEmailInput').val();
    const password = $('#loginPasswordInput').val();

    hideFormError('#loginError');

    $.ajax({
        url: API_BASE_URL + '/session',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({email: email, password: password}),
        xhrFields: {
            withCredentials: true
        }
    })
        .done(function () {
            $('#loginForm')[0].reset();
            bootstrap.Modal.getInstance($('#loginModal')[0]).hide();
            loadCurrentUser();
        })
        .fail(function (jqXHR) {
            showFormError('#loginError', getLoginErrorMessage(jqXHR.status));
        });
}

function getLoginErrorMessage(status) {
    if (status === 401) {
        return 'Неверный email или пароль';
    }
    if (status === 422) {
        return 'Проверьте правильность заполнения полей';
    }
    return 'Что-то пошло не так, попробуйте позже';
}

function logout() {
    $.ajax({
        url: API_BASE_URL + '/session', method: 'DELETE', xhrFields: {
            withCredentials: true
        }
    })
        .always(function () {
            showGuestState();
        });
}

function apiRequest(options) {
    return $.ajax(options).catch(function (jqXHR) {
        if (jqXHR.status !== 401) {
            return $.Deferred().reject(jqXHR);
        }

        return $.ajax({
            url: API_BASE_URL + '/session',
            method: 'PUT',
            xhrFields: {withCredentials: true}
        }).then(function () {
            return $.ajax(options);
        });
    });
}

function loadTasks() {
    apiRequest({
        url: API_BASE_URL + '/tasks',
        method: 'GET',
        xhrFields: {
            withCredentials: true
        }
    })
        .done(function (tasks) {
            renderTasks(tasks);
        })
        .fail(function () {
            showGuestState();
        });
}

function renderTasks(tasks) {
    $('#activeTasksList').empty();
    $('#doneTasksList').empty();

    tasks.forEach(function (task) {
        const item = buildTaskItem(task);

        if (task.is_done) {
            $('#doneTasksList').append(item);
        } else {
            $('#activeTasksList').append(item);
        }
    });
}

function buildTaskItem(task) {
    const item = $('<li class="list-group-item d-flex align-items-center gap-3"></li>');
    item.data('task', task);

    const checkbox = $('<input class="form-check-input mt-0" type="checkbox">');
    checkbox.prop('checked', task.is_done);

    const titleButton = $('<button type="button" class="btn btn-link p-0 text-decoration-none flex-grow-1 text-start task-title"></button>');
    titleButton.addClass(task.is_done ? 'text-body-secondary' : 'text-body');
    titleButton.text(task.title);

    item.append(checkbox);
    item.append(titleButton);

    return item;
}

function addTask() {
    const title = $('#newTaskTitleInput').val().trim();

    if (title === '') {
        return;
    }

    hideFormError('#taskError');

    apiRequest({
        url: API_BASE_URL + '/tasks',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({title: title}),
        xhrFields: {
            withCredentials: true
        }
    })
        .done(function () {
            $('#newTaskTitleInput').val('');
            loadTasks();
        })
        .fail(function () {
            showFormError('#taskError', 'Не удалось добавить задачу, попробуйте ещё раз');
        });
}

function toggleTask(taskId, isDone) {
    apiRequest({
        url: API_BASE_URL + '/tasks/' + taskId,
        method: 'PATCH',
        contentType: 'application/json',
        data: JSON.stringify({is_done: isDone}),
        xhrFields: {
            withCredentials: true
        }
    })
        .done(function () {
            loadTasks();
        })
        .fail(function () {
            loadTasks();
        });
}

function openTaskModal(task) {
    $('#taskIdInput').val(task.id);
    $('#taskTitleInput').val(task.title);
    $('#taskDescriptionInput').val(task.description || '');
    $('#taskDoneCheckbox').prop('checked', task.is_done);

    bootstrap.Modal.getOrCreateInstance($('#taskModal')[0]).show();
}

function saveTaskFromModal() {
    const taskId = $('#taskIdInput').val();
    const title = $('#taskTitleInput').val().trim();
    const description = $('#taskDescriptionInput').val().trim();

    if (title === '') {
        loadTasks();
        return;
    }

    apiRequest({
        url: API_BASE_URL + '/tasks/' + taskId,
        method: 'PATCH',
        contentType: 'application/json',
        data: JSON.stringify({
            title: title,
            description: description === '' ? null : description,
            is_done: $('#taskDoneCheckbox').prop('checked')
        }),
        xhrFields: {
            withCredentials: true
        }
    })
        .done(function () {
            loadTasks();
        })
        .fail(function () {
            loadTasks();
        });
}

function deleteTask(taskId) {
    apiRequest({
        url: API_BASE_URL + '/tasks/' + taskId,
        method: 'DELETE',
        xhrFields: {
            withCredentials: true
        }
    })
        .done(function () {
            loadTasks();
        })
        .fail(function () {
            loadTasks();
        });
}
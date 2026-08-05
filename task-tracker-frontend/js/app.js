const API_BASE_URL = 'http://localhost:8080';

$(function () {
    loadCurrentUser();

    $('#registerForm').on('submit', function (event) {
        event.preventDefault();
        register();
    });

    $('#loginForm').on('submit', function (event) {
        event.preventDefault();
        login();
    });
});

function loadCurrentUser() {
    $.ajax({
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
}

function showGuestState() {
    $('#userEmailLabel').text('');
    $('#userArea').addClass('d-none');
    $('#guestArea').removeClass('d-none');
    $('#mainContent').addClass('d-none');
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

const API_BASE_URL = 'http://localhost:8080';

$(function () {
    loadCurrentUser();
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
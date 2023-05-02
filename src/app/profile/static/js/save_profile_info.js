function save_login(save_profile_info_url, login) {
    let login_input = document.getElementById('login')

    if (login_input.value.length < 8 || login_input.value.length > 50) {
        toastr.warning('Login must be 8-50 characters!');
        login_input.focus()
        return;
    }

    fetch(save_profile_info_url, {
        method: "POST",
        body: JSON.stringify({login: login_input.value}),
        headers: {"Content-type": "application/json; charset=UTF-8",},
    }).then(function (response) {
        if (response.ok) {
            toastr.success('Successfully saved');
        } else {
            toastr.error('Such login already in use!');
            login_input.value = login
        }
    });
}

function save_email(save_profile_info_url, email) {
    let email_input = document.getElementById('email')
    fetch(save_profile_info_url, {
        method: "POST",
        body: JSON.stringify({email: email_input.value}),
        headers: {"Content-type": "application/json; charset=UTF-8",},
    }).then(function (response) {
        if (response.ok) {
            toastr.success('Successfully saved');
        } else {
            toastr.error('Such email already in use!');
            email_input.value = email
        }
    });
}

function change_password(change_password_url) {
    let old_password_input = document.getElementById("old-password")
    let new_password_input = document.getElementById("new-password")

    if (new_password_input.value.length < 8 || new_password_input.value.length > 50) {
        toastr.warning('Password must be 8-50 characters!');
        new_password_input.focus()
        return;
    }

    fetch(change_password_url, {
        method: "POST",
        body: JSON.stringify({
            old_password: old_password_input.value,
            new_password: new_password_input.value
        }),
        headers: {"Content-type": "application/json; charset=UTF-8",},
    }).then(function (response) {
        if (response.ok) {
            toastr.success('Successfully saved');
        } else {
            toastr.error('Wrong password');
        }
    });
}
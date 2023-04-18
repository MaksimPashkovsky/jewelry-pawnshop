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

function save_balance(save_profile_info_url) {
    toastr.options.positionClass = "toast-bottom-center";
    toastr.options.timeOut = 3000;

    const card_number = document.getElementById('card-number');
    card_number.style.borderColor = "black";
    if (card_number.value.replace(/\d{16}/, "OK") !== "OK") {
        card_number.style.borderColor = "red";
        toastr.error('Invalid card number!')
        return false;
    }

    const exp_month = document.getElementById('expiration-month')
    const exp_year = document.getElementById('expiration-year')

    exp_month.style.borderColor = "black";
    exp_year.style.borderColor = "black";

    if (exp_month.value.replace(/\d{2}/, "OK") !== "OK" || Number(exp_month.value) > 12 || Number(exp_month.value) < 1) {
        exp_month.style.borderColor = "red";
        toastr.error('Invalid month!')
        return false;
    }
    if (exp_year.value.replace(/\d{2}/, "OK") !== "OK" || Number(exp_year.value) < 23) {
        exp_year.style.borderColor = "red";
        toastr.error('Invalid year!')
        return false;
    }

    const cvv = document.getElementById('cvv');
    cvv.style.borderColor = "black";
    if (cvv.value.replace(/\d{3}/, "OK") !== "OK") {
        cvv.style.borderColor = "red";
        toastr.error('Invalid CVV!')
        return false;
    }

    const amount = document.getElementById('amount');
    amount.style.borderColor = "black";

    if (amount.value.replace(/\d+\.\d{1,2}/, "OK") !== "OK" && amount.value.replace(/\d+/, "OK") !== "OK") {
        amount.style.borderColor = "red";
        toastr.error('Invalid amount!')
        return false;
    }
    let balance = document.getElementById('balance')
    let balance_input = document.getElementById('amount')

    fetch(save_profile_info_url, {
        method: "POST",
        body: JSON.stringify({balance: Number(balance_input.value) + Number(balance.value)}),
        headers: {"Content-type": "application/json; charset=UTF-8",},
    }).then(function (response) {
        if (response.ok) {
            toastr.success('Successfully added!');
            balance.value = Number(balance_input.value) + Number(balance.value)
            setTimeout(() => {
                location.reload()
            }, 1000);
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
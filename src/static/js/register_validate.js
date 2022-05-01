function Validate() {
    toastr.options.positionClass = "toast-top-center";
    toastr.options.timeOut = 3000;

    const login = document.getElementById("login");
    const password1 = document.getElementById('password');
    const password2 = document.getElementById('password2');

    if (login.value.length < 8 || login.value.length > 50) {
        toastr.warning('Login must be 8-50 characters!');
        login.focus()
        return false;
    }
    else if (password1.value.length < 8 || password1.value.length > 50) {
        toastr.warning('Password must be 8-50 characters!');
        password1.focus()
        return false;
    }
    else if (password1.value !== password2.value) {
        toastr.warning("Password doesn't match!");
        password2.focus()
        return false;
    }
    return true;
}
function disable_card() {
    var inputs = document.getElementsByClassName('form-control');
    for (var i = 0; i < inputs.length; i++) {
        inputs.item(i).disabled = true;
    }
}

function enable_card() {
    var inputs = document.getElementsByClassName('form-control');
    for (var i = 0; i < inputs.length; i++) {
        inputs.item(i).disabled = false;
    }
}

function confirm_purchase(confirm_page_url, main_page_url) {
    toastr.options.positionClass = "toast-bottom-center";
    toastr.options.timeOut = 3000;

    if (document.getElementById('credit').checked) {

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
    }

    fetch(confirm_page_url, {
        method: "GET",
    }).then(function (response) {
        if (response.ok) {
            toastr.success('Thank you!');
            setTimeout(() => {
                window.location.replace(main_page_url)
            }, 1000);
        } else {
            toastr.warning('Not enough products!')
        }
    });
}
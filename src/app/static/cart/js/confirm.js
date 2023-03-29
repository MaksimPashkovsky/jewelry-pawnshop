function confirm_purchase(balance, total_price, confirm_page_url, main_page_url) {

    if (Number(balance) < Number(total_price)) {
        toastr.warning('Not enough money on account!');
        return;
    }

    fetch(confirm_page_url, {
        method: "GET",
    }).then(function (response) {
        if (response.ok) {
            toastr.success('Thank you!');
            setTimeout(() => { window.location.replace(main_page_url) }, 1000);
        }
        else {
            toastr.warning('Not enough products!')
        }
    });
}
function add_to_cart(id, add_to_cart_url) {
    fetch(add_to_cart_url, {
        method: "POST",
        body: JSON.stringify({ id: id, }),
        headers: { "Content-type": "application/json; charset=UTF-8", },
    }).then(toastr.success('Added to cart'));
}
function searchFunction() {
    // Declare variables
    var input, filter, container, cards, article_name, i, txtValue;
    input = document.getElementById('searchInput');
    filter = input.value.toUpperCase();
    container = document.getElementById("articlesContainer");
    cards = container.getElementsByClassName('col');

    // Loop through all list items, and hide those who don't match the search query
    for (i = 0; i < cards.length; i++) {
        article_name = cards[i].getElementsByClassName("card-title")[0];
        txtValue = article_name.textContent || article_name.innerText;
        if (txtValue.toUpperCase().indexOf(filter) > -1) {
            cards[i].style.display = "";
        } else {
            cards[i].style.display = "none";
        }
    }
}

function search() {
    var search_type = document.getElementById('search_type').value;
    var keyword = document.getElementById('keyword').value;

    var href = "/blog/list"
    if (search_type != "all"){
        href += "?tag="+search_type
        if (keyword != ""){
            href += "&keyword="+keyword
        }
    }
    else if (keyword != ""){
        href += "?keyword="+keyword
    }
    window.location.href = href;
}
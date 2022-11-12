function openNav() {
    if (document.getElementById("mySidebar").style.width == "0px") {
        document.getElementById("mySidebar").style.width = "220px";
        document.getElementById("main").style.marginLeft = "220px";
    } else {
        document.getElementById("mySidebar").style.width = "0px";
        document.getElementById("main").style.marginLeft = "0px";
    }
}
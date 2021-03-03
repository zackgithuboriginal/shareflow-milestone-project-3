$(document).ready(function(){
    $("#date-target").text(new Date().getFullYear()); 
    $("#flash-message-close").click(function(){
        this.parentNode.style.display="none"
    });
});

function displayDropdown(postId){
    let target = document.getElementById(`post-options-${postId}`)
    if (target.style.display  == "flex"){
        clearDropdowns()
        target.style.display  = "none"
    } else {
        clearDropdowns()
        target.style.display  = "flex"
    }
}

function clearDropdowns(){
    let allDropdowns = document.querySelectorAll(".post-edit-options")
    for(i = 0; i < allDropdowns.length; i++){
        allDropdowns[i].style.display = "none"
    }
}
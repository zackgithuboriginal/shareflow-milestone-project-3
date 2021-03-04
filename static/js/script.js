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

function clearComments(){
    let allComments = document.querySelectorAll(".post-comment-container")
    for(i = 0; i < allComments.length; i++){
        allComments[i].style.display = "none"
    }
}

function displayComments(postId){
    let target = document.getElementById(`post-comments-${postId}`)
    console.log(target)
    if (target.style.display  == "flex"){
        clearComments()
        target.style.display  = "none"
    } else {
        clearComments()
        target.style.display  = "flex"
    }
}
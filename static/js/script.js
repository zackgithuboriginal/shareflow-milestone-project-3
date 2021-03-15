$(document).ready(function(){
    $("#date-target").text(new Date().getFullYear()); 
    $("#flash-message-close").click(function(){
        this.parentNode.style.display="none"
    });
    truncatePosts();
});

window.onresize = truncatePosts;

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
    if (target.style.display  == "flex"){
        clearComments()
        target.style.display  = "none"
    } else {
        clearComments()
        target.style.display  = "flex"
    }
}

function clearCommentForms(){
    let allCommentForms = document.querySelectorAll(".create-comment-form")
    for(i = 0; i < allCommentForms.length; i++){
        allCommentForms[i].style.display = "none"
    }
}

function displayCommentForm(postId){
    let target = document.getElementById(`create-comment-form-${postId}`)
    if (target.style.display  == "flex"){
        clearCommentForms()
        target.style.display  = "none"
    } else {
        clearCommentForms()
        target.style.display  = "flex"
    }
}

function tabDisplay(tab){
    let tabDOM = document.getElementsByClassName("tab-display-option");
    let target = document.getElementById(`${tab}-display`);
    for(i = 0; i < tabDOM.length; i++){
        tabDOM[i].style.display = "none";
    };

    let linkDOM = document.getElementsByClassName("page-option");
    let targetLink = document.getElementById(`display-tab-${tab}`);
    for(i = 0; i < linkDOM.length; i++){
        linkDOM[i].classList.remove("active-tab");
    };
    
    targetLink.classList.add("active-tab")
    target.style.display = "flex"
}

function truncatePosts(){
    let containerWidth = $(window).width()
    let postTextArray = Array.from(document.getElementsByClassName("post-text"))
    if(containerWidth < 768){
        for (i = 0; i < postTextArray.length; i++){
            if(postTextArray[i].textContent.length > 200 && postTextArray[i].style.maxHeight != "30rem"){
                postTextArray[i].nextSibling.nextSibling.style.display = "flex";
            }
        }
    } else {
        for (i = 0; i < postTextArray.length; i++){
        postTextArray[i].nextSibling.nextSibling.style.display = "none";
        }
    }
}

function expandPost(post){
    post.previousSibling.previousSibling.style.maxHeight = "30rem"
    post.style.display = "none"
}
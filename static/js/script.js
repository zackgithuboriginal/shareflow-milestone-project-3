$(document).ready(function(){
    $("#date-target").text(new Date().getFullYear()); 
});

function displayOptions(postId){
    target = document.getElementById(`post-options-${postId}`)
    if (target.style.display  == "flex"){
        target.style.display  = "none"
    } else {
        target.style.display  = "flex"
    }
}
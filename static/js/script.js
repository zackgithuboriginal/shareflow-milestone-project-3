$(document).ready(function(){

    $(".close-avatar-modal").click(function(){
        $("#avatar-select-modal").modal('hide');
    });
    /**
     * Automatically updates footer copyright date
     */
    $("#date-target").text(new Date().getFullYear());
    /**
     * Closes flash messages on click of x button
     */ 
    $("#flash-message-close").click(function(){
        this.parentNode.style.display="none"
    });

    /**
     * Calls function to normalise post titles on page load
     */
    updatePostTopics();
    /**
     * Calls function to hide the end of posts that are too long to maintain visual clarity
     */
    truncatePosts();

    $('#direct-input-image-url').click(function(){
        document.getElementById("direct-url-input-radio").checked=true;
        document.getElementById("direct-input-image-url").required = true;
    })
    $('input[name="avatar_select"]').change(function(){
        if($('input[name="avatar_select"]:checked').val()=="direct_input"){
            console.log("hello")
            document.getElementById("direct-input-image-url").required = true;
        } else {
            document.getElementById("direct-input-image-url").required = false;
        }

    });
    
    profileTabDisplayParse();
    urlParsing();
});
window.onresize = truncatePosts;

var password = document.getElementById("password"), confirm_password = document.getElementById("repeat-password");


function validatePassword(){
  if(password.value != confirm_password.value) {
    confirm_password.setCustomValidity("Please ensure that the passwords match");
  } else {
    confirm_password.setCustomValidity('');
  }
}

password.onchange = validatePassword;
confirm_password.onkeyup = validatePassword;

function profileTabDisplayParse(){
    currentParams = new URLSearchParams(window.location.search);

    let prevUserPlusPage = "1"
    let prevUserPostPage = "1"
    let currentUserPlusPage = checkSearchParams("userPlusPage")
    let currentUserPostPage = checkSearchParams("userPostPage")

    function checkSearchParams(param){
        let currentParamPage;
        if(currentParams.has(param)){
        currentParamPage  = currentParams.get(param)
        } else{
        currentParamPage = "1"
        }
        return currentParamPage
    }

    if(document.referrer.includes("?")){
        let prevUrlFirstParam, prevUrlFirstParamValue, prevUrlSecondParam, prevUrlSecondParamValue
        prevUrl = document.referrer.split("?")[1]

        if( prevUrl.includes("&")){
            prevUrlFirstParam = prevUrl.split("&")[0].split("=")[0]
            prevUrlFirstParamValue = prevUrl.split("&")[0].split("=")[1]
            prevUrlSecondParam = prevUrl.split("&")[1].split("=")[0]
            prevUrlSecondParamValue = prevUrl.split("&")[1].split("=")[1]

            if(prevUrlFirstParam=="userPostPage"){
                prevUserPostPage=prevUrlFirstParamValue
                prevUserPlusPage=prevUrlSecondParamValue

            } else {
                prevUserPostPage=prevUrlSecondParamValue
                prevUserPlusPage=prevUrlFirstParamValue
            }

        }   else {
            prevUrlFirstParam = prevUrl.split("=")[0]
            prevUrlFirstParamValue = prevUrl.split("=")[1]

            if(prevUrlFirstParam=="userPostPage"){
                prevUserPostPage=prevUrlFirstParamValue

            } else {
                prevUserPlusPage=prevUrlFirstParamValue

            }
        }
    }
    



    if( currentUserPlusPage != prevUserPlusPage){
        tabDisplay("plusses")
    }
    if( currentUserPostPage != prevUserPostPage){
        tabDisplay("posts")
    }
}

function urlParsing(){
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    if(urlParams.has('sort-by')){
        sortCriteria = urlParams.get('sort-by')
        let sortOptions = document.getElementById('sort-by-dropdown').options
        console.log(sortOptions)
        for (i=0; i < sortOptions.length; i++){
            if (sortOptions[i].value == sortCriteria) {
                console.log(sortOptions[i].value);
                sortOptions.selectedIndex = i;
            }
        }
    }
    if(urlParams.has('topic')){
        topic = urlParams.get('topic')
        let topicOptions = document.getElementById('filter-dropdown').options
        console.log(topicOptions)
        for (i=0; i < topicOptions.length; i++){
            if (topicOptions[i].value == topic) {
                console.log(topicOptions[i].value);
                topicOptions.selectedIndex = i;
        }
    }
}
}

/**
 * This function handles the display of the post edit options dropdown menu
 */
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

/**
 * This function clears all of the post edit option dropdowns to ensure no more than one displays at a time
 */
function clearDropdowns(){
    let allDropdowns = document.querySelectorAll(".post-edit-options")
    for(i = 0; i < allDropdowns.length; i++){
        allDropdowns[i].style.display = "none"
    }
}



/**
 * This function toggles the display of a post's comments
 */
function displayComments(e, postId, idLocation){
    let target = document.getElementById(`${idLocation}${postId}`)
    let eventTrigger = e.srcElement
    let commentCount = eventTrigger.textContent.slice(eventTrigger.textContent.length -4);
    console.log(commentCount)
    if (target.style.display  == "flex"){
        clearComments()
        target.style.display  = "none"
        eventTrigger.textContent=`Show Comments ${commentCount}`
    } else {
        clearComments()
        target.style.display  = "flex"
        eventTrigger.textContent=`Hide Comments ${commentCount}`
    }
}

/**
 * This function closes any opened comment sections
 */
function clearComments(){
    let allComments = document.querySelectorAll(".post-comment-container")
    for(i = 0; i < allComments.length; i++){
        allComments[i].style.display = "none"
    }
}


/**
 * This function toggles the create comment form when the button is clicked
 */
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

/**
 * This function closes all open comment forms
 */
function clearCommentForms(){
    let allCommentForms = document.querySelectorAll(".create-comment-form")
    for(i = 0; i < allCommentForms.length; i++){
        allCommentForms[i].style.display = "none"
    }
}


/**
 * This function controls which profile tab is active and displayed
 */
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



/**
 * This function loops through all posts and if they exceed a defined character length and the page is small enough it will hide the end of the post and display a toggleable button
 */
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

/**
 * This function handles displaying a post at its full length when the expand button is selected
 */
function expandPost(post){
    post.previousSibling.previousSibling.style.maxHeight = "30rem"
    post.style.display = "none"
}


/**
 * This function will loop through all post topics and capitalise them
 */
function updatePostTopics(){
    postTopics = document.getElementsByClassName("post-topic")
    console.log(postTopics)
        for (i = 0; i < postTopics.length; i++){
            postTopics[i].textContent = postTopics[i].textContent.replace("-"," ")
        }
}


function formSubmit() {
    let url = document.forms["avatar-submit-form"].elements["avatar_direct_input"].value;
    if (!checkURL(url)) {
        alert("Invalid URL. Please submit a URL with one of the following extensions: jpeg, jpg, gif, png.");
        return(false);
    }
    testImage(url, function(testURL, result) {
        if (result == "success") {
            document.forms["avatar-submit-form"].submit();
        } else if (result == "error") {
            alert("The URL given does not point to the correct type of image.");
        } else {
            alert("The image URL was not reachable. Check that the URL is correct.");
        }

    });
    return(false);
}

function checkURL(url) {
    return(url.match(/\.(jpeg|jpg|gif|png)$/) != null);
}

function testImage(url, callback, timeout) {
    timeout = timeout || 5000;
    let timedOut = false, timer;
    let img = new Image();
    img.onerror = img.onabort = function() {
        if (!timedOut) {
            clearTimeout(timer);
            callback(url, "error");
        }
    };
    img.onload = function() {
        if (!timedOut) {
            clearTimeout(timer);
            callback(url, "success");
        }
    };
    img.src = url;
    timer = setTimeout(function() {
        timedOut = true;
        callback(url, "timeout");
    }, timeout); 
}

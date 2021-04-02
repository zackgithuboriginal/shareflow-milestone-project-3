$(document).ready(function(){

    
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

    currentPage = window.location.pathname

    /**
     * When the active page is account.html, posts.html or post_details.html
     * the functions in this statement will be called
     */
    if ((currentPage.indexOf("account") !== -1) || (currentPage.indexOf("posts") !== -1) || (currentPage.indexOf("post_details") !== -1) ) {
        /**
         * Calls function to normalise post topics on page load
         */
        updatePostTopics();
        /**
         * Calls function to hide the end of posts that are too long to maintain visual clarity
         */
        truncatePosts();
    }

    /**
     * When the avatar selection modal of account.html is open and the url input option is selected
     * this will make entering a url required and will apply the active style to the input field
     */
    $('#direct-input-image-url').click(function(){
        document.getElementById("direct-url-input-radio").checked=true;
        document.getElementById("direct-input-image-url").required = true;
    })
    
    /**
     * This function handles removing the required attribute from the direct input field
     * when another radio option is selected
     */
    $('input[name="avatar_select"]').change(function(){
        if($('input[name="avatar_select"]:checked').val()=="direct_input"){
            document.getElementById("direct-input-image-url").required = true;
        } else {
            document.getElementById("direct-input-image-url").required = false;
        }
    });
    
    /**
     * When the active page is account.html
     * the functions in this statement will be called
     */
    if (currentPage.indexOf("account") !== -1) {
        /**
         * Calls a function which reads the url to determine which account tab needs to be open upon pagination reload
         */
        profileTabDisplayParse();
        /**
         * This function hides the modal whenever the 'x' or close buttons are clicked
         */
        $(".close-avatar-modal").click(function(){
            $("#avatar-select-modal").modal('hide');
        });
    }
    /**
     * When the active page is posts.html
     * this function will be called to read the filter and sort arguments from the url and display the current conditions in the select inputs
     */
    if (currentPage.indexOf("posts") !== -1) {
        urlParsing();
    }
});


/**
 * This will call the truncatepost function to shorten posts that exceed a certain length
 * when the page is resized due to different length requirements at different sizes
 */
window.onresize = truncatePosts;

/**
 * This function validates that both the password inputs in the registration form are the same
 * It takes their values, compares them and if they don't match applies a validity message
 */
function passwordValidation(){
    let password = document.getElementById("password"), confirm_password = document.getElementById("repeat-password");

    function validatePassword(){
    if(password.value != confirm_password.value) {
        confirm_password.setCustomValidity("Please ensure that the passwords match");
    } else {
        confirm_password.setCustomValidity('');
    }
    }
}


/**
 * This function is called when the account page is loaded,
 * it's primary purpose is to work out which of the account display tabs should be open 
 * by comparing the current url and page parameter arguments with those of the referring url
 * The value of the argument that has changed will reflect which tab was interacted with and will inform the tab that should be active
 */
function profileTabDisplayParse(){
    currentParams = new URLSearchParams(window.location.search);

    /**
     * Default values in case the referring url was from a different page, not a reload due to pagination
     */
    let prevUserPlusPage = "1"
    let prevUserPostPage = "1"

    let currentUserPlusPage = checkSearchParams("userPlusPage")
    let currentUserPostPage = checkSearchParams("userPostPage")

    /**
     * Basic function to determine a current value for arguments of both tabs
     */
    function checkSearchParams(param){
        let currentParamPage;
        if(currentParams.has(param)){
        currentParamPage  = currentParams.get(param)
        } else{
        currentParamPage = "1"
        }
        return currentParamPage
    }

    /**
     * If statement to ensure the document referrer contains a query before continuing in logic
     */
    if(document.referrer.includes("?")){
        let prevUrlFirstParam, prevUrlFirstParamValue, prevUrlSecondParam, prevUrlSecondParamValue

        /**
         * Splits and isolates the query section from referrer
         * i.e 'https://shareflow-milestone-project-3.herokuapp.com/account/None?userPlusPage=2&userPostPage=2' to 'userPlusPage=2&userPostPage=2'
         */
        prevUrl = document.referrer.split("?")[1]

        /**
         * If two parameters are present in url, splits them , and the further splits to seperate name of arg from value
         * i.e 'userPlusPage=2&userPostPage=2'
         * =>     'userPlusPage=2'
         * =>     'userPlusPage' and '2'
         */
        if( prevUrl.includes("&")){
            prevUrlFirstParam = prevUrl.split("&")[0].split("=")[0]
            prevUrlFirstParamValue = prevUrl.split("&")[0].split("=")[1]
            prevUrlSecondParam = prevUrl.split("&")[1].split("=")[0]
            prevUrlSecondParamValue = prevUrl.split("&")[1].split("=")[1]

            /**
             * This section assigns values to the variables representing the previous url's argument values
             */
            if(prevUrlFirstParam=="userPostPage"){
                prevUserPostPage=prevUrlFirstParamValue
                prevUserPlusPage=prevUrlSecondParamValue

            } else {
                prevUserPostPage=prevUrlSecondParamValue
                prevUserPlusPage=prevUrlFirstParamValue
            }

        /**
         * If thers only one argument then the string is split and values to the variables representing the previous url's argument values
         */
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

    /**
     * Compares the previous and current parameter values for each parameter
     * if there's a change then that is set as active tab
     */
    if( currentUserPlusPage != prevUserPlusPage){
        tabDisplay("plusses")
    }
    if( currentUserPostPage != prevUserPostPage){
        tabDisplay("posts")
    }
}

/**
 * Function handles reading the url to inform the active filter and sort select elements
 */
function urlParsing(){
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);

    /**
     * If there is a sort argument in url, it will apply the selected attribute to that option
     */
    if(urlParams.has('sort-by')){
        sortCriteria = urlParams.get('sort-by')
        let sortOptions = document.getElementById('sort-by-dropdown').options
        for (i=0; i < sortOptions.length; i++){
            if (sortOptions[i].value == sortCriteria) {
                sortOptions.selectedIndex = i;
            }
        }
    }
    /**
     * If there is a filter argument in url, it will apply the selected attribute to that option
     */
    if(urlParams.has('topic')){
        topic = urlParams.get('topic')
        let topicOptions = document.getElementById('filter-dropdown').options
        for (i=0; i < topicOptions.length; i++){
            if (topicOptions[i].value == topic) {
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
 * This function will loop through all post topics and replace hyphens with spaces for readability
 */
function updatePostTopics(){
    postTopics = document.getElementsByClassName("post-topic")
        for (i = 0; i < postTopics.length; i++){
            postTopics[i].textContent = postTopics[i].textContent.replace("-"," ")
        }
}

/**
 * Function that is called when the avater submit form is submitted
 * It's purpose is to handle validating that the directly input url is both a valid url 
 * and that it relates to an image
 */
function formSubmit() {
    let url = document.forms["avatar-submit-form"].elements["avatar_direct_input"].value;
    if (!checkURL(url)) {
        alert("Invalid URL. Please submit a URL with one of the following extensions: jpeg, jpg, gif, png.");
        return(false);
    }
    /**
     * Calls function to test the url to determine that it relates to an image
     * passes callback function as parameter to handle the result
     */
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

/**
 * Using regex to read the url and determine if it has the correct file extension
 */
function checkURL(url) {
    return(url.match(/\.(jpeg|jpg|gif|png)$/) != null);
}

/**
 * Function that analyses whether the url relates to an image
 * Attempts to load it as an img element
 * if it loads image returns success
 * if it timesout it returns timeout
 * if it fails to load as an image returns error
 */
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
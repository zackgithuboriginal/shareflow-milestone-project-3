# Shareflow - Milestone Project 3

![Image of responsive page mockups](https://github.com/zackgithuboriginal/shareflow-milestone-project-3/blob/master/static/images/readme_images/device-mockup.PNG)

## Website Description
This website is designed to be a location for people to share their thoughts and opinions on a range of topics and to interact and engage with other users and their posts. Designing the website I intended to maximise the clarity and visibility of the user’s content and the ease and usability of interaction and navigation above all other considerations. 

The thinking behind this process was that as a social media/ message board the content and the ease of creating, navigating and filtering that content would be integral to the user experience of the website. In order to pursue this ideal the website has a number of features aimed to elevate the importance and visibility of user’s posts and to allow them to view and interact with the posts in a number of different ways.

## User Experience / UX
### First time visitor
To be able to understand the purpose of the site

To be able to understand the navigation structure and how to interact with the website

To be able to register an account to enable them to post

### Return user 
To be able to log in

To be able to be to make a post

To be able to edit their post

To be able to delete their post if desired

To be able to comment on other people’s posts

To be able to show support for a post

### General user

To be able to only view posts relating to certain topics

### Site administrators
To be able to delete any posts

### Design

#### Design Overview
There were two driving principles behind the design were firstly to create an environment in which there is a clear hierarchy of importance with user’s content and posts being foremost in importance and secondly to create an easily understandable and intuitive navigation and interaction interface.

#### Colour Scheme
![Image of responsive page mockups](https://github.com/zackgithuboriginal/shareflow-milestone-project-3/blob/master/static/images/readme_images/shareflow-primary-colour-scheme.png)
#### Primary Colours
These three colours are the primary colours of the website, they make up the background colours of the majority of visual elements on the page. The three primary colours, are, as above in the image #FFFFFF, #89A6FB and #1B263B. 

#89A6FB is used as the main branding colour of the website. This colour was chosen as it’s a very calm colour that wouldn’t be too distracting or too eye catching for the user. As well as that, as a purple shade, when it is combined with white text it creates a minimal and in my opinion very clean aesthetic. This aesthetic was something that I really valued and placed importance on as creating a clean interface with clear hierarchical importance was something I valued in the design of this project. 

#FFFFFF, or plain white was used to highlight elements that were related to of central importance to the user or to the page that they were on. For instance, on the Home page, the elements that hold the most importance to the user were, the post filtering and sorting options as well as the posts themselves. These elements therefore, are primarily white, which when contrasted against #1B263B, a dark navy colour, and the background colour of each page stand out very clearly and immediately pop into the eye of the user. 

As a user scrolls down the page or navigates through the website their eye is immediately drawn to the most important information and most important points of interaction which is an feature that was very important to achieve to help the user understand and feel comfortable using the site and browsing the site’s content.

![Image of responsive page mockups](https://github.com/zackgithuboriginal/shareflow-milestone-project-3/blob/master/static/images/readme_images/shareflow-topics-colour-scheme.png)

#### Secondary colours in use in the site exist to create a distinction between posts relating to different topics. I decided to undertake this route, with a clear visual cue indication the post’s topic as I believed that it could foster an almost subconscious and very quick understanding of a post’s content and allow a user who was scrolling through the website to quickly find posts that might interest them without necessarily having to use the filtering functionality.

#### Typography
The two fonts in use in the website are Montserrat and Libre Franklin. These two fonts are visibly distinct although both were chosen as clean, minimal and easy to read fonts. Montserrat is used throughout the site in areas that needed to be highlighted and set apart in times of importance and visibility. It is used in navigation elements, headings and titles as well as in form elements. Libre Franklin on the other hand is a more visually simple font and so is used in paragraph elements and other locations were the user would be expected to read a longer section of text. 

#### Imagery
There aren’t many images used in the website. Following the idea of being more of a message board than a typical social media website the features and functionality of the website are primarily centered around the sharing of ideas and text, as opposed to the sharing of imagery.
There are however user avatars and pictures. Whenever a user registers an account they are given a placeholder avatar. If they then go to the account page they are able to either choose a different avatar or enter a url linking to an image that they wish to use. After they submit the form their account image will be updated and on any post that they make their image will be displayed. 

The user’s image is also displayed on the user’s account page itself, alongside some of the user’s profile statistics and information in order to encourage the user to create a sense of identity and ownership with the account.

### Wireframes

The wireframes for the website were developed using [Figma](https://www.figma.com/)


## Features

### Home Page

![Image of responsive page mockups](https://github.com/zackgithuboriginal/shareflow-milestone-project-3/blob/master/static/images/readme_images/home_page.png)

The home page has two major roles. Firstly, it’s role is to introduce the user to the website and enable them to understand it’s purpose and functionality. Secondly the home page is the primary means of exploring user’s posts and discovering new ideas and discussions.

In order to achieve the first goal I aimed to make the purpose of the home page as simple and clear as possible. Upon loading the page the user is presented with a column of posts down the center of the page with a toolbar just above them with options to filter and sort. The user upon interacting with the scrollable list of posts will get an idea of the purpose of the site and will understand that this is an environment for creating and sharing posts.

The second goal of the home page to be the primary post navigation screen is achieved by utilising a number of smaller features to make the functionality of viewing and exploring posts as convenient and intuitive as possible.

### Post Filter and Sort Toolbar
![Image of responsive page mockups](https://github.com/zackgithuboriginal/shareflow-milestone-project-3/blob/master/static/images/readme_images/filter-feature.PNG)

At the top of the home page is a toolbar containing two dropdown options that allow users to customise the appearance and display of posts in order to improve the page’s practical usability and make it more user friendly. The User can both sort and filter the posts displayed. The options for sorting posts are to sort by date created, which is the default setting of the page and which will display the newest posts at the top of the page with older ones chronologically below it, or by most popular. The Most popular sort uses the voting system attached to each post and sorts the posts from most votes tallied to least. This is a very useful tool to find the most interesting or engaging posts as opposed to just the newest and can provide a very different post browsing experience.
The filter options for the posts, allow the user to display all of the posts, across all topics, or by one of the five topics provided. The five topics being Sports, Entertainment, Global News, Politics and General Thoughts. This filtering functionality allows the user to explore posts relating to one topic that may interest them in particular and increases the usefulness of the post display.

### Pagination 
![Image of responsive page mockups](https://github.com/zackgithuboriginal/shareflow-milestone-project-3/blob/master/static/images/readme_images/pagination-features.PNG)

The home page makes use of pagination to display only a certain number of posts at a time to the user. It does this for a couple of reasons. Number one, instead of displaying all of the posts initially and forcing the user’s browser to load them all at once, which would be increasingly impractical if there was a large number of posts it will load the posts 10 at a time to lower the demand on the browser. Number two it will allow a user to easily navigate back and forth between the pages to find posts that they like without having to scroll and search for the post.

### Create post floating action button
![Image of responsive page mockups](https://github.com/zackgithuboriginal/shareflow-milestone-project-3/blob/master/static/images/readme_images/fab-feature.PNG)

This floating action button is a fixed element on the bottom right of the screen. Since it is fixed it will stay in position even as a user scrolls down the page. When the user hovers over the button a label will appear with the text ‘Create a Post’, and when the user clicks the button the page will be redirected directly to the Create a Post page. This button is there to add another option to navigate to the post creation page, and provides an option for mobile users to create a post without having to reach to the top of the screen which can be inconvenient and un ergonomic.

### Create post page
![Image of responsive page mockups](https://github.com/zackgithuboriginal/shareflow-milestone-project-3/blob/master/static/images/readme_images/create_post_page.png)

The create post page is very simple and consists of a single form titled ‘Post Details’. The form is where the user can input the details of the post. The form contains an input box for the title, a textarea input for the post content and a dropdown selection for the post topic. The dropdown selection is populated with the five topics available. To ensure that the website’s posts both maintain a consistent size on the page as well as to ensure that the posts maintain a reasonable standard of effort there are minimum character requirements for both the title and the post content. When the user submits the page they will automatically be directed to the home page and the newest posts.

### Edit Post Page
![Image of responsive page mockups](https://github.com/zackgithuboriginal/shareflow-milestone-project-3/blob/master/static/images/readme_images/edit_post_page.png)

The edit post page is similar to the the create post page, it contains a form in the same format and styling. When a user selects the option to edit their post, the page loads with the existing details of the post prefilled and editable. When the user has edited the post to their satisfaction they can submit and they will be redirected to the posts details page for that post.


### 404 Page
![Image of responsive page mockups](https://github.com/zackgithuboriginal/shareflow-milestone-project-3/blob/master/static/images/readme_images/404_page.png)

In the event that a user attempts to navigate to a page that either does not exist or has been deleted the flask routing will redirect them to the 404 response page. This page is very basic and acts as a landing page in the case of a load error. It consists of a header text explaining that the page the user has tried to load doesn’t exist and a subheading providing a countdown to when the page will automatically redirect to the home page. The subheading also contains a link to the home page in the case that the page does not automatically redirect. 

### Sign in / Registration Page 

![Image of responsive page mockups](https://github.com/zackgithuboriginal/shareflow-milestone-project-3/blob/master/static/images/readme_images/sign_in_page.png)
![Image of responsive page mockups](https://github.com/zackgithuboriginal/shareflow-milestone-project-3/blob/master/static/images/readme_images/register_page.png)

The sign in and registration pages are mirrored versions of themselves. They consist of a central card containing a form, in the case of the sign in page, consisting of two input fields one for their username and one for their password and in the case of the registration form three fields one for their desired username, one for their intended password and another to repeat their password for validation. In the case that the user submits a username that is not available or that they submit passwords that are not matching they will receive a validation message informing them that their input does not meet the requirements. 

### Post Details Page
![Image of responsive page mockups](https://github.com/zackgithuboriginal/shareflow-milestone-project-3/blob/master/static/images/readme_images/post_details_page.png)

The post details page is where a post is displayed when a user selects the ‘View Post’ option from either their profile or from the home page. The page contains the same information as the regular post view with the basic post details as well as the voting button. Additionally there is a close button on the top right of the card which will return the user to the page that they were on remembering the pagination status of that page.

As well as the post details the page contains a comment section that will display the total comment count if there are any otherwise it will display a placeholder message. The section contains a form where a user can submit a comment and then below that the comments of the post are displayed in chronological order starting with the oldest.


### Account Page
![Image of responsive page mockups](https://github.com/zackgithuboriginal/shareflow-milestone-project-3/blob/master/static/images/readme_images/account_page.png)

The user’s account page is unique to them and generated using data gathered from their interaction with the website and with other user’s posts. The page consists of two sections, the first is the account details section where the user’s username is displayed along with their avatar or chosen image and a display of some statistics relating to the user’s engagement with the website. 
The second section is the post display container. The post display container consists of a toggleable display that will either display the posts authored by the user, which is the default display or the posts ‘plussed’ by the user. The idea behind the toggleable display is to allow the user to view their own posts or to view the posts that they had plussed. This is a useful feature that practically allows a user to save posts that they want to view again in the future simply by voting for it.

### Account details
![Image of responsive page mockups](https://github.com/zackgithuboriginal/shareflow-milestone-project-3/blob/master/static/images/readme_images/account_details.PNG)

This is the account details display, it takes values from the user’s database record to inform the total posts made total comments and total votes received. It also displays the length of time since the account was registered.


### Display tab
![Image of responsive page mockups](https://github.com/zackgithuboriginal/shareflow-milestone-project-3/blob/master/static/images/readme_images/display_tab.PNG)

There are two display tabs one for users posts and one for posts that the user has voted for. They are displayed in paginated lists and the page will only display one tab at a time. To ensure user experience is as seamless and intuitive as possible the page will remember the status of both pagination lists as well as the active tab whenever the page reloads or a user navigates back to the page from the post details page.

### Avatar Selection
![Image of responsive page mockups](https://github.com/zackgithuboriginal/shareflow-milestone-project-3/blob/master/static/images/readme_images/avatar_select.PNG)

Whenever the user clicks on the account image in the account details section of their account page, a modal will display with a radio selection option of either selecting one of a number of provided avatars or selecting the option to input a url that leads to an image of their choice. The url input will automatically validate that the url relates to an image and that the url loads an image successfully. If it does not, the user will be alerted that the url they entered is not valid. This avatar will be displayed on all posts authored by the user to create a sense of a community of people as opposed to just anonymous posts.

### Flash messages
![Image of responsive page mockups](https://github.com/zackgithuboriginal/shareflow-milestone-project-3/blob/master/static/images/readme_images/flash_message.PNG)

Whenever a user takes an action that causes the page to update or reload such as commenting, editing a post, signing in, signout etc. The page will display a message in the center of the screen informing the user of the success or the failure of the action.

### Post Card
![Image of responsive page mockups](https://github.com/zackgithuboriginal/shareflow-milestone-project-3/blob/master/static/images/readme_images/post-feature.PNG)

The Post card itself is the primary way in which a post is displayed. The post contains a plus which can be clicked on to vote on the post, this will also enable the post to be displayed in the plussed posts tab of the user’s account page. an button which will navigate the user to the post details page for that post 

### Logical routing behaviour
There are some interactions with the site that in order to provide a satisfying and logical experience for the user needs to recall the user’s previous actions. The most complex example of this is when a user on their account page changes the active tab of the account page and changes the active page of the pagination menu, then proceeds to navigate into the post details page of a post and open up the edit post page for that post. In this instance the website will recall the previous user’s path to the page and the account page’s pagination and tab arguments from when the user was last on the page. To ensure satisfying user experience the page will return the user to the post details page when the edit page is closed and then return the user to the account page with the correct pagination status and with the correct tab open when the user closes the post details page.

## You must format your buttons in a very specific way so that they provide the proper calls to the routes I made. It really isn't that specific to be honest, you just need to make sure you go read my routes within `peakpass_routes.py`. For example, the login button will need to have an href point to `/login`, the logout button will need to point to `/logout`, and the sign up button needs to point to `/sign-up`. That's basically all you need to know. I handle loading the web pages when they are needed, for example the 404 page.

## Below is a list of all of the pages that you need to create as of now.
* index.html (The main webpage)
* login.html
* login-incorrect.html (The same exact as login, except add a little message that shows that they entered the wrong login information)
* sign-up.html (Sign up page for new users)
* signup-success.html (Same as the login page, except add a little green confirmation message showing that their account has been made and they can now log in)
* signup-failure.html (Same as the sign-up.html page but with a little message that shows the email is already in use)
* sign-up.html
* 404.html

## Also please create a sort of default template page that can be used to fill in all of the technical information for the project. This will also double as the same template that will be used to give more user friendly information about overall web security.
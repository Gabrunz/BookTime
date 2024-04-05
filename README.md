
#  BookTime a CS50x - Final Project

 
Hello, my name is Gabriele Mora, I’m from Cividate Camuno a small city in Italy.

Booktime is a web application developed for the CS50x final project using Flask, enabling users to explore, track, and review books. The platform integrates with the New York Times API to showcase trending bestsellers in both fiction and non-fiction categories and use the Google Book API for all the books cover and all the books information available in the project.


###  Video Demo: <https://youtu.be/sMj3HBIK3Y4>

  

##  Features

  

-  **Trending Books** - Fetches and displays trending books using the New York Times API and Google Books API.

-  **Book Information** - Provides detailed information on each book, including covers, authors, and a description of the book.

-  **User Library** - Allows users to manage their library, mark books as read or to-be-read.

-  **Reviews** - Enables users to publish and view book reviews, along with average ratings for each book.

  
  

##  Dependencies

List of dependencies required to run this project:

-  **Flask** - Web framework for Python.

-  **Flask-Login** - Provides user session management.

-  **Werkzeug** - Handles password hashing and authentication.

-  **SQLAlchemy** - ORM (Object-Relational Mapping) for database operations.

-  **datetime** - Module for manipulating dates and times.

-  **Statistics** - Module for statistical operations.

-  **json** - Handles JSON data.

-  **urllib** - Library for handling URLs.

##  Installation


1. Clone this repository.

2. Install dependencies with `pip install -r requirements.txt`.

3. Set up the database with appropriate configurations.

4. Run the Flask server with `python main.py`.

  

##  Usage

  

1. Start the Flask server with execution of the `main.py`.
2. Add your NYT API (you can get it here: https://developer.nytimes.com) and a SECRET KEY 

3. Access the URL `http://localhost:5050` in your browser.

  

##  Files and directories
In the booktime folder we can find: 
 - JSON
	 - fiction.json - File that have the tranding list of best seller fiction books of the week based on the NYT API
	 - non_fiction.json - File that have the tranding list of best seller non-fiction books of the week based on the NYT API
- STATIC
	- IMAGES - Folder with images of the 6 categories in the homepage + the not found image when a coverbook is not available on Google Books API
	- script.js - File with a script to disable the search button on mobile if no word in the search box
	- style.css - Different CSS settings for Navbar and Card
- TEMPLATES
	-  base.html - File with Bootstrap navbar and flask flash message system for error or success
	-  book.html - The book page with different Jinja control if user is authenticated or if user have the book in the library
	- category.html - Page with for loop for show the best 40 books in the category
	- index.html - Homepage with trading section and category section
	- library.html - Page available only when logged in that show all the books added in your library and the book readed
	- login.html - A simple login page with redirect for sign-up if not registred
	- search.html - Page that show the books finded when used the search box in the navbar
	- settings.html - Page available only when logged in and permits to change the name, email and the password of the account
	- sign-up.html - Page for make an account if not existing 

 - \_\_init\_\_.py - Python file with Secret Key to add for security use and all configuration and blueprints for render the pages
 - auth.py - Python file with login, logout, sign-up route
 - models.py - Python file with models for database (Book, User and Review)
 - views.py - Most important file of the project contains most of the route(book, homepage, search etc.) and have different function inside

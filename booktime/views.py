from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from urllib.request import urlopen
from datetime import datetime, timedelta
from .models import User, Book, Review
from . import db
from sqlalchemy import select, update, and_, insert, delete
from datetime import datetime
from statistics import mean 
import json


views = Blueprint("views", __name__)


@views.route("/")
def home():
    api_nyt = "#ADD_HERE_YOUR_NYT_API_KEY" 

    # read file if exist else create a new local file fiction and non_fiction
    with open("booktime/json/fiction.json", "r+") as fiction_trending:
        data_best_seller_fiction = json.loads(fiction_trending.read())
        fiction_last_update_sring = data_best_seller_fiction["last_modified"][0:19]
        fiction_last_update = datetime.strptime(
            fiction_last_update_sring, "%Y-%m-%dT%H:%M:%S"
        )
        deltatime = timedelta(days=-7)
        if fiction_last_update - datetime.now() < deltatime:
            response = urlopen(
                "https://api.nytimes.com/svc/books/v3/lists.json?list=combined-print-and-e-book-fiction&api-key="
                + api_nyt
            )
            data = response.read().decode("utf-8")
            data_best_seller_fiction = json.loads(data)

            for i in range(0, 5):
                isbn = data_best_seller_fiction["results"][i]["book_details"][0][
                    "primary_isbn13"
                ]
                search_book = urlopen(
                    "https://www.googleapis.com/books/v1/volumes?q=+isbn:" + isbn
                )
                book = json.load(search_book)

                search_items = book.get("items", [])
                if not search_items:
                    cover_book = "/static/images/categories/not_found.jpeg"
                    data_best_seller_fiction["results"][i]["book_details"][0][
                        "primary_isbn13"
                    ] = None

                else:
                    cover_book = book["items"][0]["volumeInfo"]["imageLinks"][
                        "thumbnail"
                    ]

                data_best_seller_fiction["results"][i]["book_details"][0][
                    "book_cover"
                ] = cover_book
                fiction_trending.truncate(0)
                fiction_trending.seek(0)
                fiction_trending.write(json.dumps(data_best_seller_fiction))

    with open("booktime/json/non_fiction.json", "r+") as non_fiction_trending:
        data_best_seller_nonfiction = json.loads(non_fiction_trending.read())
        non_fiction_last_update_sring = data_best_seller_nonfiction["last_modified"][
            0:19
        ]
        non_fiction_last_update = datetime.strptime(
            non_fiction_last_update_sring, "%Y-%m-%dT%H:%M:%S"
        )
        deltatime = timedelta(days=-7)
        if non_fiction_last_update - datetime.now() < deltatime:
            response = urlopen(
                "https://api.nytimes.com/svc/books/v3/lists.json?list=combined-print-and-e-book-nonfiction&api-key="
                + api_nyt
            )
            data = response.read().decode("utf-8")
            data_best_seller_nonfiction = json.loads(data)

            for i in range(0, 5):
                isbn = data_best_seller_nonfiction["results"][i]["book_details"][0][
                    "primary_isbn13"
                ]
                search_book = urlopen(
                    "https://www.googleapis.com/books/v1/volumes?q=+isbn:" + isbn
                )
                book = json.load(search_book)

                search_items = book.get("items", [])
                if not search_items:
                    cover_book = "/static/images/categories/not_found.jpeg"
                    data_best_seller_nonfiction["results"][i]["book_details"][0][
                        "primary_isbn13"
                    ] = None

                else:
                    cover_book = book["items"][0]["volumeInfo"]["imageLinks"][
                        "thumbnail"
                    ]

                data_best_seller_nonfiction["results"][i]["book_details"][0][
                    "book_cover"
                ] = cover_book
                non_fiction_trending.truncate(0)
                non_fiction_trending.seek(0)
                non_fiction_trending.write(json.dumps(data_best_seller_nonfiction))

    return render_template(
        "index.html",
        user=current_user,
        best_seller_nonfiction=data_best_seller_nonfiction,
        best_seller_fiction=data_best_seller_fiction,
    )



@views.route("/book/<isbn>", methods=["POST", "GET"])
def book_info(isbn):
    api_googlebooks_search = "https://www.googleapis.com/books/v1/volumes?q=+isbn:"

    def add_book():
        if check_book() == False:
            book = Book(isbn=isbn, user_id=current_user.get_id(), page_readed=0)
            db.session.add(book)
            db.session.commit()

    def delete_book():
        delete = (
            db.session.query(Book)
            .filter(
                and_(Book.isbn.like(isbn), Book.user_id.like(current_user.get_id()))
            )
            .delete()
        )
        db.session.commit()

    def check_book():
        check_num = (
            db.session.query(Book)
            .filter(
                and_(Book.isbn.like(isbn), Book.user_id.like(current_user.get_id()))
            )
            .count()
        )
        if check_num == 1:
            return True
        else:
            return False

    def check_completed():
        completed = (
            db.session.query(Book.page_readed)
            .filter(
                and_(Book.isbn.like(isbn), Book.user_id.like(current_user.get_id()))
            )
            .scalar()
        )
        if completed == 100:
            return True
        else:
            return False

    def mark_as_completed():
        stmt = (
            update(Book)
            .where(and_(Book.isbn == isbn, Book.user_id == current_user.get_id()))
            .values(page_readed=100)
        )
        db.session.execute(stmt)
        db.session.commit()

    def mark_as_to_be_read():
        stmt = (
            update(Book)
            .where(and_(Book.isbn == isbn, Book.user_id == current_user.get_id()))
            .values(page_readed=0)
        )
        db.session.execute(stmt)
        db.session.commit()

    def publish_review(star_review, text_review):
        if check_book() == True:
            if user_review() == None:
                if star_review != None:
                    review = Review(book_id=isbn, user_id=current_user.get_id(), star_review = star_review, text = text_review)
                    db.session.add(review)
                    db.session.commit()
                    flash("Review published", category="success")
                else:
                    flash("Select a star rating", category="error")
            else: 
                flash("Review already published", category="error")

    def counter_review():
        row = db.session.execute(select(Review.star_review).where(Review.book_id == isbn)).all()
        star_ratings = [item[0] for item in row]
        return star_ratings
    
    def average_review():
        if len(counter_review()) != 0:
            return round(mean(counter_review()), 1)
        else:
            return 0

    def all_review():
        all_review = db.session.execute(select(User.full_name, Review.time_created, Review.star_review, Review.text).join(User).where(Review.book_id == isbn)).all()
        return all_review

    def user_review(): #Return None if not found
        user_review = db.session.execute(select(Review.star_review, Review.text).where(Review.book_id == isbn, Review.user_id == current_user.get_id())).first()
        return user_review
    
    def delete_review():
        delete_review_query = delete(Review).where(Review.book_id == isbn, Review.user_id == current_user.get_id())
        db.session.execute(delete_review_query)
        db.session.commit()        
        
    serach_response = urlopen(api_googlebooks_search + isbn)
    search = json.load(serach_response)

    for i in range(len(search["items"])):
        dict_check = search["items"][i]["volumeInfo"]
        if dict_check.get("imageLinks") is None:
            search["items"][i]["volumeInfo"]["imageLinks"] = {
                "thumbnail": "/static/images/categories/not_found.jpeg"
            }
        if dict_check.get("authors") is None:
            search["items"][i]["volumeInfo"]["authors"] = ""
        if dict_check.get("publishedDate") is None:
            search["items"][i]["volumeInfo"]["publishedDate"] = ""
        if dict_check.get("categories") is None:
            search["items"][i]["volumeInfo"]["categories"] = ""

    if request.method == "POST":
        if request.form.get("add_book") == "ADD_BOOK":
            add_book()
        elif request.form.get("delete_book") == "DELETE_BOOK":
            delete_book()
        elif request.form.get("book_completed") == "BOOK_COMPLETED":
            mark_as_completed()
        elif request.form.get("mark_as_to_be_read") == "MARK_AS_TO_BE_READ":
            mark_as_to_be_read()

        if request.form.get("publish_review") == "PUBLISH_REVIEW":
            star_review = request.form.get("starReview")
            text_review = request.form.get("textReview")
            publish_review(star_review, text_review)

        if request.form.get("delete_review") == "DELETE_REVIEW":
            delete_review()


    if current_user.is_authenticated:
        return render_template(
            "book.html",
            user=current_user,
            search=search,
            book_in_library=check_book(),
            completed=check_completed(),
            number_of_review=len(counter_review()), 
            average_review= average_review(),
            reviews = all_review(),
            user_review = user_review()
        )
    else:
        return render_template("book.html", user=current_user, search=search, number_of_review=len(counter_review()), average_review= average_review(), reviews = all_review())


@views.route("/search")
def search():
    search_input = request.args.get("q").encode("ascii", "ignore").decode("utf-8")
    api_googlebooks_search = "https://www.googleapis.com/books/v1/volumes?q="
    safe_input = search_input.replace(" ", "+")

    if safe_input == "":
        return redirect(url_for("views.home"))
        flash("No input", category="error")

    serach_response = urlopen(api_googlebooks_search + safe_input)
    search = json.load(serach_response)

    for i in range(len(search["items"])):
        dict_check = search["items"][i]["volumeInfo"]
        if dict_check.get("imageLinks") is None:
            search["items"][i]["volumeInfo"]["imageLinks"] = {
                "thumbnail": "/static/images/categories/not_found.jpeg"
            }

        if dict_check.get("authors") is None:
            search["items"][i]["volumeInfo"]["authors"] = ""

        if dict_check.get("publishedDate") is None:
            search["items"][i]["volumeInfo"]["publishedDate"] = ""

        if dict_check.get("industryIdentifiers") is None:
            search["items"][i]["volumeInfo"]["industryIdentifiers"] = ""

    return render_template(
        "search.html", search=search, user=current_user, search_input=search_input
    )


@views.route("/category/<category_name>")
def categories(category_name):
    api_googlebooks_search = "https://www.googleapis.com/books/v1/volumes?q=subject:"

    serach_response = urlopen(api_googlebooks_search + category_name + "&maxResults=40")
    search = json.load(serach_response)

    for i in range(len(search["items"])):
        dict_check = search["items"][i]["volumeInfo"]
        if dict_check.get("imageLinks") is None:
            search["items"][i]["volumeInfo"]["imageLinks"] = {
                "thumbnail": "/static/images/categories/not_found.jpeg"
            }
        if dict_check.get("authors") is None:
            search["items"][i]["volumeInfo"]["authors"] = ""
        if dict_check.get("publishedDate") is None:
            search["items"][i]["volumeInfo"]["publishedDate"] = ""
        if dict_check.get("industryIdentifiers") is None:
            search["items"][i]["volumeInfo"]["industryIdentifiers"] = ""

    return render_template(
        "category.html", search=search, category_name=category_name, user=current_user
    )


@views.route("/library")
def library():
    # Get ID, Search For Books and then see if completed or to be read
    user_id = current_user.get_id()

    results = db.session.query(Book.isbn).filter(Book.user_id == user_id).all()
    api_googlebooks_search = "https://www.googleapis.com/books/v1/volumes?q=+isbn:"

    books_isbn = [
        result[0] for result in results
    ]  # Convert multiple tuples in single elements and put in a list
    number_of_book = len(books_isbn)

    books = []
    for i in range(number_of_book):
        serach_response = urlopen(api_googlebooks_search + books_isbn[i])
        search = json.load(serach_response)

        dict_check = search["items"][0]["volumeInfo"]
        if dict_check.get("imageLinks") is None:
            search["items"][0]["volumeInfo"]["imageLinks"] = {
                "thumbnail": "/static/images/categories/not_found.jpeg"
            }

        if dict_check.get("authors") is None:
            search["items"][0]["volumeInfo"]["authors"] = ""

        if dict_check.get("publishedDate") is None:
            search["items"][0]["volumeInfo"]["publishedDate"] = ""

        if dict_check.get("industryIdentifiers") is None:
            search["items"][0]["volumeInfo"]["industryIdentifiers"] = ""

        completed = (
            db.session.query(Book.page_readed)
            .filter(
                and_(
                    Book.isbn.like(books_isbn[i]),
                    Book.user_id.like(current_user.get_id()),
                )
            )
            .scalar()
        )
        if completed == 100:
            search["items"][0]["volumeInfo"]["pageReaded"] = 100
        else:
            search["items"][0]["volumeInfo"]["pageReaded"] = 0

        books.append(search)

    return render_template(
        "library.html", search=books, user=current_user, number_of_book=number_of_book
    )


@views.route("/settings", methods=["POST", "GET"])
@login_required
def settings():
    def correctly_modified(stmt):
        db.session.execute(stmt)
        db.session.commit()
        flash("Changes saved correctly", category="success")
        return redirect(url_for("views.home"))
    
    def something_wrong():
        return redirect(url_for("views.settings"))

    if request.method == "POST":
        full_name = request.form.get("fullName")
        email = request.form.get("email")
        old_password = request.form.get("oldPassword")
        password = request.form.get("password")
        password2 = request.form.get("password2")
        user = User.query.filter_by(email=email).first()


        if full_name != "":
            if len(full_name) < 4:
                flash("Full name must be greater than 4 characters", category="error")
                return something_wrong()

        if email != "":
            if len(email) < 4:
                flash("Email must be greater than 4 characters", category="error")
                something_wrong()
            elif user == email:
                flash("Email already in our system", category="error")
                return something_wrong()

        if old_password != "" or password != "" or password2 != "":
            if old_password != "" and password != "" and password2 != "":
                if not check_password_hash(current_user.password, old_password):
                    flash("Old password don't match", category="error")
                    return something_wrong()
            else:
                flash("Password is missing", category="error")
                return something_wrong()
                


        if len(password) < 7:
            flash("Password must be greater than 7 characters", category="error")
            return something_wrong()

        if password != password2:
            flash("Passwords don't match", category="error")
            return something_wrong()

        hashed_password = generate_password_hash(password, method="scrypt")

        if full_name != "" and email != "":
            if old_password == "" and password == "" and password2 == "":
                stmt = (
                    update(User)
                    .where(User.id == current_user.get_id())
                    .values(full_name=full_name, email=email)
                )
            else:
                stmt = (
                    update(User)
                    .where(User.id == current_user.get_id())
                    .values(full_name=full_name, email=email, password=hashed_password)
                )
            correctly_modified(stmt)
        elif full_name != "" and email == "":
            if old_password == "" and password == "" and password2 == "":
                stmt = (
                    update(User)
                    .where(User.id == current_user.get_id())
                    .values(full_name=full_name)
                )
            else:
                stmt = (
                    update(User)
                    .where(User.id == current_user.get_id())
                    .values(full_name=full_name, password=hashed_password)
                )
            correctly_modified(stmt)
        elif full_name == "" and email != "":
            if old_password == "" and password == "" and password2 == "":
                stmt = (
                    update(User)
                    .where(User.id == current_user.get_id())
                    .values(email=email)
                )
            else:
                stmt = (
                    update(User)
                    .where(User.id == current_user.get_id())
                    .values(email=email, password=hashed_password)
                )
            correctly_modified(stmt)
        elif full_name == "" and email == "":
            if old_password == "" and password == "" and password2 == "":
                flash("Nothing changed", category="error")
            else:
                stmt = (
                    update(User)
                    .where(User.id == current_user.get_id())
                    .values(password=hashed_password)
                )
                correctly_modified(stmt)
        else:
            flash("Something is wrong...", category="error")
            something_wrong()
            
    
    
    return render_template("settings.html", user=current_user)

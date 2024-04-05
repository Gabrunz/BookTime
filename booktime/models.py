from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(20))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    time_created = db.Column(db.DateTime(timezone=True), default=func.now())
    page_readed = db.Column(db.Integer)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(300), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    books = db.relationship("Book")

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.String(20), db.ForeignKey('book.isbn'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    star_review = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text)
    time_created = db.Column(db.DateTime(timezone=True), default=func.now())

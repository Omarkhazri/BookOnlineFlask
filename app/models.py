from . import db
from flask_login import UserMixin

# Define User model
class User(UserMixin,db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(255), nullable=False)
    def __repr__(self):
        return f'{self.username}'
# Define Book models
class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), nullable=False)
    language_id = db.Column(db.Integer, db.ForeignKey('languages.id'), nullable=False)
    title = db.Column(db.String(255))
    desc = db.Column(db.Text)
    num_pages = db.Column(db.Integer)
    publication_date = db.Column(db.Date)
    download_link = db.Column(db.Text)
    img_path = db.Column(db.Unicode(128))
    author = db.relationship('Author', backref='books')
    language = db.relationship('Language', backref='books')

    def __repr__(self):
        return f'{self.title}'

# Define Author model
class Author(db.Model):
    __tablename__ = 'authors'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    author_name = db.Column(db.String(255))
    def __repr__(self):
        return f'{self.author_name}'
# Define Author model
class Language(db.Model):
    __tablename__ = 'languages'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code_lang = db.Column(db.String(3))
    def __repr__(self):
        return f'{self.code_lang}'
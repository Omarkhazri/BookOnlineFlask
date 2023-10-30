from app import db
from app.routes import app
from app.models import User
from app.models import Book
from app.models import Author
from app.models import Language
@app.shell_context_processor
def make_shell_context():
    return dict(db=db,User=User,Book=Book,Author=Author,Language=Language)
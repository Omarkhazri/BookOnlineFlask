import os
from . import create_app
from .models import User,Book,Author,Language
from . import db
from flask import redirect, request, abort, render_template, url_for,flash
from flask_admin import Admin,form
from flask_admin.contrib.sqla import ModelView
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager,login_user,login_required, current_user, logout_user
from sqlalchemy.event import listens_for
from markupsafe import Markup
import os
import os.path as op

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

# Create directory for file fields to use
file_path = op.join(op.dirname(__file__), 'files')
try:
    os.mkdir(file_path)
except OSError:
    pass

with app.app_context():
    db.create_all()

admin = Admin(app, name='BookOnlineAdmin', template_mode='bootstrap4')

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return User.query.get(int(user_id))

@listens_for(Book, 'after_delete')
def del_image(mapper, connection, target):
    if target.path:
        # Delete image
        try:
            os.remove(op.join(file_path, target.path))
        except OSError:
            pass

        # Delete thumbnail
        try:
            os.remove(op.join(file_path,
                              form.thumbgen_filename(target.path)))
        except OSError:
            pass


class BookView(ModelView):
    form_columns = ('title','desc','language', 'num_pages', 'publication_date', 'download_link', 'author','img_path')
    def _list_thumbnail(view, context, model, name):
        if not model.img_path:
            return ''

        return Markup('<img src="%s">' % url_for('static',filename=form.thumbgen_filename(model.img_path)))

    column_formatters = {
        'img_path': _list_thumbnail
    }

    # Alternative way to contribute field is to override it completely.
    # In this case, Flask-Admin won't attempt to merge various parameters for the field.
    form_extra_fields = {
        'img_path': form.ImageUploadField('Image',
                                      base_path=file_path,
                                      thumbnail_size=(100, 100, True))
    }
    
class ExcluedBookView(ModelView):
    form_excluded_columns = ('books')     

admin.add_view(ModelView(User, db.session))
admin.add_view(BookView(Book, db.session))
admin.add_view(ExcluedBookView(Author, db.session))
admin.add_view(ExcluedBookView(Language, db.session))

@app.route("/")
def index():
    books = Book.query.all()
    return render_template("index.html", books=books,form=form)


@app.route("/profile")
@login_required
def profile():
    return render_template("user/profile.html", user=current_user)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template("auth/login.html")

@app.route('/login', methods=['POST'])
def login_post():
    # login code goes here
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('login')) # if the user doesn't exist or password is wrong, reload the page
    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect(url_for('index'))

@app.route('/register')
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template("auth/register.html")

@app.route('/register', methods=['POST'])
def register_post():
    # code to validate and add user to database goes here
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')

    # if this returns a user, then the email already exists in database
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User.query.filter_by(username=username).first()

    if user: # if a user is found, we want to redirect back to signup page so user can try again
        flash('Email address already exists')
        return redirect(url_for('register'))

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    new_user = User(username=username, email=email, password=generate_password_hash(password))

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('login'))

@app.route("/book/<int:id>", methods=["GET"])
def get_book(id):
    book = Book.query.get(id)
    if book is None:
        abort(404)
    return render_template("book/book.html", book=book,form=form)

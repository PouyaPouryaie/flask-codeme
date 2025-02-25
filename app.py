from flask import Flask, render_template, flash, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired, EqualTo, Length
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user

app = Flask(__name__)

# Create key for CSRF protection
app.config['SECRET_KEY'] = "this is my secret key for test"

# Add SQLite database
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

# Add MySQL database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123@localhost/our_users'

#Initialize database
db = SQLAlchemy(app)

# initialize Migrate
migrate = Migrate(app, db)

# initialize LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

### Login Area ###
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()

        if user:
            # check password
            if user.verify_password(form.password.data):
                login_user(user)
                flash("Login successful!!!")
                return redirect(url_for("dashboard"))
            else:
                flash("Worng Password, Try Again!!!")
        else:
            flash("That username doesn't exist, Try Again!!!")

    return render_template("login.html", form=form)


@app.route("/logout", methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("You Have been logged out!")
    return redirect(url_for("login"))

### Login Area End ###

### Blog Post Area ###
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.now)
    slug = db.Column(db.String(255))

class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = StringField("Content", validators=[DataRequired()], widget=TextArea())
    author = StringField("Author", validators=[DataRequired()])
    slug = StringField("Slug",validators=[DataRequired()])
    submit = SubmitField("Submit")

@app.get('/posts')
def posts():
    # Grab all the posts from the database
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template('posts.html', posts=posts)

@app.route('/posts/add', methods=['GET', 'POST'])
def add_post():
    form = PostForm()

    if request.method == 'POST' and form.validate_on_submit():
        post = Posts(title=request.form['title'], content=request.form['content'], author=request.form['author'], slug=request.form['slug'])
        
        # clear form
        form.title.data = ''
        form.content.data = ''
        form.author.data = ''
        form.slug.data = ''
        
        # add to db
        db.session.add(post)
        db.session.commit()

		# Return a Message
        flash("Blog Post Submitted Successfully!")

	# Redirect to the webpage
    return render_template("add_post.html", form=form)

@app.route('/posts/<int:id>', methods=['GET'])
def get_post(id):
    post = Posts.query.get_or_404(id)
    return render_template("post.html", post=post)

@app.route('/posts/update/<int:id>', methods=['GET', 'POST'])
def update_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()

    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.author = form.author.data
        post.slug = form.slug.data
        db.session.commit()
        flash("Post Has Been Updated!")
        return redirect(url_for("get_post", id=id))
    
    form.title.data = post.title
    form.content.data = post.content
    form.author.data = post.author
    form.slug.data = post.slug
    return render_template("edit_post.html", form=form, id=id)

@app.route("/posts/delete/<int:id>", methods=['GET'])
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)

    try:
        db.session.delete(post_to_delete)  # Use the instance!
        db.session.commit()
        flash("Post was Deleted!")
        return redirect(url_for('posts'))
    except Exception as e:
        db.session.rollback() # Important: Rollback on error
        flash(f"There was a problem deleting the post: {e}") # Include error message
        return redirect(url_for('posts'))



### Blog Post Area End ###

### Dashboard Area ###
@app.route("/dashboard", methods=['GET', 'POST'])
@login_required
def dashboard():
    form = UserForm()
    id = current_user.id
    user_to_update = Users.query.get_or_404(id)

    if request.method == 'POST':
        user_to_update.full_name = request.form['full_name']
        user_to_update.username = request.form['username']
        user_to_update.email = request.form['email']
        user_to_update.favorite_color = request.form['favorite_color']
        try:
            db.session.commit()
            flash("User Updated successfully!")
            return render_template('dashboard.html', form=form, user_to_update=user_to_update)
        except Exception as e:
            db.session.rollback()
            flash(f"There was a problem updating the User: {e}")
            return render_template('dashboard.html', form=form, user_to_update=user_to_update)
    else:
        return render_template('dashboard.html', form=form, user_to_update=user_to_update)

### Dashboard Area End ###

# Create Model
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(255), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    favorite_color = db.Column(db.String(120))
    date_added = db.Column(db.DateTime, default=datetime.now)
    password_hash = db.Column(db.String(255))

    @property
    def password(self):
        raise AttributeError('password is not readable attribute!')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    # Create A String
    def __repr__(self):
        return '<Full Name %r>' % self.full_name

# Create the database tables (run this only once, or when you change your models)
# Important! Use app context when working with the db outside of a route
# with app.app_context(): 
#    db.create_all()
#    print("Tables created!")

# Create a UserForm Class
class UserForm(FlaskForm):
    full_name = StringField("Full Name", validators=[DataRequired()])
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    favorite_color = StringField("Favorite Color")
    password_hash = PasswordField("Password", validators=[DataRequired(), EqualTo('password_hash_confirmed', message='password is not match with confirmed password')])
    password_hash_confirmed = PasswordField("Confirmed Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


# Create userForm Page
@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    full_name = None
    email = None
    username = None
    favorite_color = None
    form = UserForm()

    # Validate the form
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            user = Users(full_name=form.full_name.data, username=form.username.data, email=form.email.data, favorite_color=form.favorite_color.data, password = form.password_hash.data)
            db.session.add(user)
            db.session.commit()
        full_name = form.full_name.data
        form.full_name.data = ''
        username = form.username.data
        form.username.data = ''
        email = form.email.data
        form.email.data = ''
        favorite_color = form.favorite_color.data
        form.favorite_color.data = ''
        form.password_hash.data = ''
        form.password_hash_confirmed.data = ''

        flash("User Added submitted successfully!") # push message to the form

    our_users = Users.query.order_by(Users.date_added)
    return render_template('add_user.html', full_name=full_name, username=username, email=email, favorite_color=favorite_color, form=form, our_users = our_users)

# update userForm
@app.route('/user/update/<int:id>', methods=['GET', 'POST'])
def update_user(id):
    form = UserForm()
    user_to_update = Users.query.get_or_404(id)

    if request.method == 'POST':
        user_to_update.full_name = request.form['full_name']
        user_to_update.username = request.form['username']
        user_to_update.email = request.form['email']
        user_to_update.favorite_color = request.form['favorite_color']
        try:
            db.session.commit()
            flash("User Updated successfully!")
            return render_template('update_user.html', form=form, user_to_update=user_to_update)
        except Exception as e:
            db.session.rollback()
            flash(f"There was a problem updating the User: {e}")
            return render_template('update_user.html', form=form, user_to_update=user_to_update)
    else:
        return render_template('update_user.html', form=form, user_to_update=user_to_update) 


# Delete userForm
@app.get('/user/delete/<int:id>')
def delete_user(id):
    user_to_delete = Users.query.get_or_404(id)
    full_name = None
    username=None
    email = None
    favorite_color = None
    form = UserForm()
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User deleted successfully!")
        our_users = Users.query.order_by(Users.date_added)
        return render_template('add_user.html', full_name=full_name, username=username, email=email, favorite_color=favorite_color, form=form, our_users = our_users)
    except Exception as e:
        db.session.rollback()
        flash(f"There was a problem deleting the User: {e}")
        our_users = Users.query.order_by(Users.date_added)
        return render_template('add_user.html', full_name=full_name, username=username, email=email, favorite_color=favorite_color, form=form, our_users = our_users)

# Create a Form Class
class ClassForm(FlaskForm):
    name = StringField("What's your name?", validators=[DataRequired()])
    submit = SubmitField("Submit")

# Create name Page
@app.route('/name', methods=['GET', 'POST'])
def name():
    name = None
    form = ClassForm()

    # Validate the form
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash("Form submitted successfully!") # push message to the form

    return render_template('name.html', name=name, form=form)

@app.route('/', methods=['GET'])
def index():
    items = ["Pepperoni", "cheese", "Mushrooms", 41]
    first_name = "Pouya"
    stuff = "this is blod text"
    return render_template("index.html", favorite_pizza=items, first_name=first_name, stuff=stuff)

@app.route('/date')
def return_json_format_date():
    return { "Date": datetime.now() }

@app.get('/user/<string:user>')
def get_user(user):
    return render_template("user.html", user_name=user)

# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html", error=e), 404 # 404 tells Flask that the status code of that page should be 404 which means not found

@app.errorhandler(500)
def server_error(e):
    return render_template("500.html", error=e), 500 # 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)


# {{}} is used for variables & {% %} is used for logic such as for loops, if statements 
# run the app: flask --app app run or python3 app.py
# Flask-WTF -> https://flask-wtf.readthedocs.io/en/1.2.x/quickstart/#creating-forms
# WTFforms Fields -> https://wtforms.readthedocs.io/en/3.2.x/fields/#field-definitions
# if you want to use css class in flask_wtf, you just in pase the class as parameter to them (eg: name.html) -> `{{ form.submit(class="btn btn-primary") }}`
# to read flash messages in HTML, you have to write a for loop on get_flashed_messages() -> {% for message in get_flashed_messages() %}
# to create database for our app use app.app_context(): db.create_all()
# for mysql you had to install pymysql and cryptography and use pymysql in connection string 
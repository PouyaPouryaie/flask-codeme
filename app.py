from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate

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

# Create Model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    favorite_color = db.Column(db.String(120))
    date_added = db.Column(db.DateTime, default=datetime.now)
    
    # Create A String
    def __repr__(self):
        return '<Name %r>' % self.name

# Create the database tables (run this only once, or when you change your models)
# Important! Use app context when working with the db outside of a route
# with app.app_context(): 
#    db.create_all()
#    print("Tables created!")

# Create a UserForm Class
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    favorite_color = StringField("Favorite Color")
    submit = SubmitField("Submit")


# Create userForm Page
@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    email = None
    favorite_color = None
    form = UserForm()

    # Validate the form
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            user = Users(name=form.name.data, email=form.email.data, favorite_color=form.favorite_color.data)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        email = form.email.data
        form.email.data = ''
        favorite_color = form.favorite_color.data
        form.favorite_color.data = ''

        flash("User Added submitted successfully!") # push message to the form

    our_users = Users.query.order_by(Users.date_added)
    return render_template('add_user.html', name=name, email=email, favorite_color=favorite_color, form=form, our_users = our_users)


# update userForm
@app.route('/user/update/<int:id>', methods=['GET', 'POST'])
def update_user(id):
    form = UserForm()
    user_to_update = Users.query.get_or_404(id)

    if request.method == 'POST':
        user_to_update.name = request.form['name']
        user_to_update.email = request.form['email']
        user_to_update.favorite_color = request.form['favorite_color']
        try:
            db.session.commit()
            flash("User Updated successfully!")
            return render_template('update_user.html', form=form, user_to_update=user_to_update)
        except:
            flash("Error! Please Try Again!")
            return render_template('update_user.html', form=form, user_to_update=user_to_update)
    else:
        return render_template('update_user.html', form=form, user_to_update=user_to_update) 


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
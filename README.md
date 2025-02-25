## Flask
This is a simple web application that show simple principles of Flask Framework


### Flask Shell
You can check your code using flask shell. for that you just need to follow these steps:
- open terminal and navigate to the project directory
- write flask shell and press enter
- import module or class from specific python file
- write code and check resutl in flask shell

## Flask Form
requirements are: Flask-WTF, WTForms -> [Documentation](https://flask-wtf.readthedocs.io/en/1.2.x/)


## Flask Login
requirements are: flask-login -> [Flask-Login](https://flask-login.readthedocs.io/en/latest/)
- To use Flask-Login, create a `LoginManager` instance and pass your Flask application (`app`) to it.
- To restrict access to any route (allowing only authorized users), add the `@login_required` decorator above the method definition.
    - The second approach involves checking whether the current_user is authenticated on the specific page using `{% if current_user.is_authenticated %}`. If the user is authenticated, the page is displayed; otherwise, an error message and a link to the login page are shown.
- To reload the user object from the user ID stored in the session, you must provide a `user_loader` callback.
    - This requires defining a method that retrieves a user from the database and decorating it with `@login_manager.user_loader`
- After successful login, pass the user entity to the `login_user(user)` function provided by Flask-Login. For logout, use the `logout_user()` function, also from Flask-Login
- To make implementing a user class easier, you can inherit from `UserMixin`, which provides default implementations for all of these properties and methods

## Note
- For migration:
    - Install Flask-Migrate
    - update your changes on models
    - import `Migrate` from `flask_migrate`
    - add this line to your code: `migrate = Migrate(app, db)`
    - run `flask db init` command
    - initialize migration: `flask db migrate -m 'Initial Migration'`
    - to push migration to database: `flask db upgrade`
- For Password Hash:
    - use Werkzeug liberary and import `generate_password_hash` and `check_password_hash` from `werkzeug.security`
    - define method and use generate_password_hash to change raw password to encrypted password
        - options: change method of encryption: `method='pbkdf2:sha256'`
- For Return Json at Flask:
    - you just need to produce a dictionary result, flask will return json object automatically

### Requirements
- MySQL: `docker run --name flask-mysql -e MYSQL_ROOT_PASSWORD=123 -p 3306:3306 -d mysql:9.2.0`
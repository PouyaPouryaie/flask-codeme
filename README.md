## Flask
This is a simple web application that show simple principles of Flask Framework


### Flask Shell
You can check your code using flask shell. for that you just need to follow these steps:
- open terminal and navigate to the project directory
- write flask shell and press enter
- import module or class from specific python file
- write code and check resutl in flask shell


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
## Flask
This is a simple web application that show simple principles of Flask Framework


## Note
- For migration:
    - Install Flask-Migrate
    - update your changes on models
    - import `Migrate` from `flask_migrate`
    - add this line to your code: `migrate = Migrate(app, db)`
    - run `flask db init` command
    - initialize migration: `flask db migrate -m 'Initial Migration'`
    - to push migration to database: `flask db upgrade`
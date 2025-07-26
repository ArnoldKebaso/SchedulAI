from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def register_db(app):
    db.init_app(app)
    # Import models so migrations detect them
    import database.models  # noqa
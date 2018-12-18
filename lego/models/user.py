"""The model for a user in the database."""

from lego import db


__all__ = ['User']


class User(db.Model):
    """User."""
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), index=True, unique=True,
                         nullable=False)
    password = db.Column(db.String(80), nullable=False)
    is_judge = db.Column(db.Boolean, default=False, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    @staticmethod
    def authenticate(username: str, password: str):
        user = User.query.filter_by(username=username).first()
        error_msg = 'Invalid credentials. Please try again.'

        if user is None:
            return error_msg

        if user.password != password:
            return error_msg

        return user

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return '<User id={!r}, username={!r}>'.format(self.id, self.username)

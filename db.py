import os
from datetime import datetime
import shutil

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

PATH_TO_FILES = 'files'

db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), index=True, nullable=False, unique=True)
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(128), index=True, nullable=False, unique=True)
    confirmed = db.Column(db.Boolean, nullable=False)
    status = db.Column(db.String(10), nullable=False, unique=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {} {} {}>'.format(self.username, self.email, self.status)


class Operation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_operation_id = db.Column(db.String(1000), index=True, nullable=False, unique=True)
    timestamp = db.Column(db.DateTime, nullable=True, default=datetime.utcnow())

    def __repr__(self):
        return '<Operation {} {}>'.format(self.user_operation_id, self.timestamp)


def update_session(*args):
    for el in args:
        db.session.add(el)
    db.session.commit()


def job_delete_inactive():
    ops = Operation.query.all()
    for op in ops:
        last_activity = op.timestamp
        uoid = op.user_operation_id
        if float(datetime.timestamp(datetime.utcnow())) - float(datetime.timestamp(last_activity)) > 10800:
            delete_folder(uoid)
            db.session.delete(op)
            update_session()


def delete_folder(name):
    path = os.path.join(PATH_TO_FILES, name)
    if os.path.exists(path):
        shutil.rmtree(os.path.join(PATH_TO_FILES, name))


def to_db(name):
    op = Operation.query.filter_by(user_operation_id=name).first()
    if op is None:
        op = Operation(user_operation_id=name)
    op.timestamp = datetime.utcnow()
    update_session(op)

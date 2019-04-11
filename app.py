import os

from flask import Flask, render_template, redirect, flash, url_for, session, request, abort
from flask import send_from_directory, make_response
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename
import uuid


from loginform import LoginForm
from regform import RegForm
from file_upload import PictureForm, AudioForm, VideoForm, ArchiveOpenForm
from db import db, User, update_session
from system_function import create_folder
from convert_functions import PictureConverter, VideoConverter, AudioConverter
from archive_functions import ArchiveFuncs

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///converter.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.app = app
db.init_app(app)
db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@app.before_request
def before_request():
    if 'user_operation_id' not in session:
        session['user_operation_id'] = uuid.uuid4().hex


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    return render_template('main.html', title='Converter')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or user.check_password(form.password.data) is False:
            flash('Invalid Username or password')
            return redirect(url_for('login'))
        else:
            login_user(user)
            flash('Logged in successfully.')
            return redirect(url_for('index'))
    return render_template('login.html', form=form, title='Authorization')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


# noinspection PyArgumentList
@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first() is not None:
            flash('Username is busy')
            return redirect(url_for('registration'))
        elif User.query.filter_by(email=form.email.data).first() is not None:
            flash('Email is busy')
            return redirect(url_for('registration'))
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        update_session(user)
        flash('Account created successful!')
        return redirect(url_for('login'))
    return render_template('registration.html', form=form, title='Registration')


@app.route('/archive-open', methods=['GET', 'POST'])
def open_archive():
    form = ArchiveOpenForm()
    if form.validate_on_submit():
        operation_id = session.get('user_operation_id')
        if operation_id is None:
            session['user_operation_id'] = uuid.uuid4().hex
            operation_id = session.get('user_operation_id')
        path_to_folder = create_folder(operation_id)
        filename = secure_filename(form.file.data.filename)
        form.file.data.save(os.path.join(path_to_folder, filename))
        arc = ArchiveFuncs(path_to_folder, filename)
        arc.extract_archive()
        files, filename = arc.all_files()
        return render_template('open-arc.html', files=files.get('files'), filename=filename)
    return render_template('open-arc.html', form=form)


# TODO: Check types
@app.route('/picture-convert', methods=['GET', 'POST'])
def convert_picture():
    form = PictureForm()
    if form.validate_on_submit():
        operation_id = session.get('user_operation_id')
        if operation_id is None:
            session['user_operation_id'] = uuid.uuid4().hex
            operation_id = session.get('user_operation_id')
        path_to_folder = create_folder(operation_id)
        filename = secure_filename(form.field.data.filename)
        form.field.data.save(os.path.join(path_to_folder, filename))
        converter = PictureConverter(path_to_folder, filename)
        files = converter.convert(form.format.data)
        return render_template('result.html', path_files=files)
    return render_template('convert.html', form=form)


@app.route('/audio-convert', methods=['GET', 'POST'])
def convert_audio():
    form = AudioForm()
    if form.validate_on_submit():
        operation_id = session.get('user_operation_id')
        if operation_id is None:
            session['user_operation_id'] = uuid.uuid4().hex
            operation_id = session.get('user_operation_id')
        path_to_folder = create_folder(operation_id)
        filename = form.field.data.filename
        form.field.data.save(os.path.join(path_to_folder, filename))
        converter = AudioConverter(path_to_folder, filename)
        converter.convert(form.format.data)
        return render_template('result.html')
    return render_template('convert.html', form=form)


@app.route('/video-convert', methods=['GET', 'POST'])
def convert_video():
    form = VideoForm()
    if form.validate_on_submit():
        operation_id = session.get('user_operation_id')
        if operation_id is None:
            session['user_operation_id'] = uuid.uuid4().hex
            operation_id = session.get('user_operation_id')
        path_to_folder = create_folder(operation_id)
        filename = form.field.data.filename
        form.field.data.save(os.path.join(path_to_folder, filename))
        converter = VideoConverter(path_to_folder, filename)
        converter.convert(form.format.data)
        return redirect(url_for('download'))
    return render_template('convert.html', form=form)


if __name__ == '__main__':
    app.run(port=8080, debug=True)

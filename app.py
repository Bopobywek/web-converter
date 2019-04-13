import os
import uuid
import datetime

from flask import Flask, render_template, redirect, flash, \
    url_for, session, send_from_directory, request
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_apscheduler import APScheduler
from flask_login import LoginManager, login_user, \
    current_user, logout_user, login_required
from werkzeug.utils import secure_filename

from archive_functions import ArchiveFuncs, ARCHIVE_SUPPORTED_FORMATS
from convert_functions import PictureConverter, VideoConverter, AudioConverter, Converter
from db import db, User, update_session, Operation
from file_upload import PictureForm, AudioForm, VideoForm, \
    ArchiveOpenForm, ArchiveConvertForm, ArchiveConvertForm2
from loginform import LoginForm
from regform import RegForm
from system_function import create_folder, get_file_type
from config import Config


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///converter.db'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
app.config.from_object(Config())
db.app = app
db.init_app(app)
db.create_all()
admin = Admin(app)
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Operation, db.session))

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@app.errorhandler(413)
def limit(e):
    if current_user.is_authenticated:
        flash('Max file size is 400 MB', category='error')
    else:
        flash('Max file size for unauthorized users is 100 MB', category='error')
    return redirect(request.referrer)


@app.before_request
def before_request():
    check_operation_id()
    app.config['MAX_CONTENT_LENGTH'] = 400 * 1024 * 1024 if \
        current_user.is_authenticated else 100 * 1024 * 1024


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
        if user is None:
            flash('User not found', category='danger')
            return redirect(url_for('registration'))
        elif user.check_password(form.password.data) is False:
            flash('Invalid Username or password', category='danger')
            return redirect(url_for('login'))
        else:
            login_user(user)
            flash('Logged in successfully', category='success')
            return redirect(url_for('index'))
    for errors in form.errors.values():
        for error in errors:
            flash(error, category='danger')
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
        flash('Already logged in', category='danger')
        return redirect(url_for('index'))
    form = RegForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first() is not None:
            flash('Username is busy', category='danger')
            return redirect(url_for('registration'))
        elif User.query.filter_by(email=form.email.data).first() is not None:
            flash('Email is busy', 'error')
            return redirect(url_for('registration'))
        user = User(username=form.username.data, email=form.email.data, status='user')
        user.set_password(form.password.data)
        update_session(user)
        flash('Account created successful!', category='success')
        return redirect(url_for('login'))
    for errors in form.errors.values():
        for error in errors:
            flash(error, category='danger')
    return render_template('registration.html', form=form, title='Registration')


@app.route('/archive-open', methods=['GET', 'POST'])
def open_archive():
    form = ArchiveOpenForm()
    if form.validate_on_submit():
        check_operation_id()
        operation_id = session.get('user_operation_id')
        path_to_folder = create_folder(operation_id)
        filename = save_file(form.file.data.filename, path_to_folder, form.file.data)
        if filename is None:
            return redirect(url_for('index'))
        arc = ArchiveFuncs(path_to_folder, filename)
        result = arc.extract_archive()
        if isinstance(result, tuple):
            flash('Sorry, an unknown error occurred', category='danger')
            return redirect(url_for('index'))
        files, filename = arc.all_files()
        return render_template('open-arc.html', files=files.get('files'), filename=filename, title='Archive Open')
    for errors in form.errors.values():
        for error in errors:
            flash(error, category='danger')
    return render_template('open-arc.html', form=form, title='Archive Open')


@app.route('/archive-convert', methods=['GET', 'POST'])
def convert_archive():
    form = ArchiveConvertForm()
    form2 = ArchiveConvertForm2()
    archive_filename = None
    if form.validate_on_submit():
        check_operation_id()
        operation_id = session.get('user_operation_id')
        path_to_folder = create_folder(operation_id)
        filename = save_file(form.file.data.filename, path_to_folder, form.file.data)
        if filename is None:
            return redirect(url_for('index'))
        arc = ArchiveFuncs(path_to_folder, filename)
        result = arc.extract_archive()
        if isinstance(result, tuple):
            flash('Sorry, an unknown error occurred. Please try again later.', category='danger')
            return redirect(url_for('index'))
        files, archive_filename = arc.all_files()
        return render_template('convert-arc.html', files=files.get('files'), filename=archive_filename,
                               get_file_type=get_file_type, arc_formats=ARCHIVE_SUPPORTED_FORMATS, form2=form2,
                               title='Archive Convert')
    if form2.validate_on_submit():
        dict_of_files = request.form.to_dict()
        files = list(filter(lambda x: os.path.exists(x), dict_of_files.keys()))
        for el in files:
            el_of_paths = el.split('/')
            path = '/'.join(el_of_paths[:-1])
            file = el_of_paths[-1]
            converter = Converter(path, file, dict_of_files[el])
            result = converter.convert()
            if bool(result):
                flash('Sorry, {} error occurred, but the archive can be successfully created.'
                      ' Please note that there may be broken content'.format(len(result)), category='warning')
            archive_filename = uuid.uuid4().hex if archive_filename is None else archive_filename
            arc_converter = ArchiveFuncs(os.path.join('files', session.get('user_operation_id')),
                                         archive_filename)
            path_new = arc_converter.make_archive(dict_of_files['arc'])
            if isinstance(path_new, str):
                el_path_new = path_new.split('/')
                file_new = el_path_new[-1]
                return render_template('result.html', path=path_new, new_filename=file_new, title='Download')
            else:
                flash('Sorry, an unknown error occurred', category='danger')
            return redirect(url_for('index'))
        archive_filename = uuid.uuid4().hex if archive_filename is None else archive_filename
        arc_converter = ArchiveFuncs(os.path.join('files', session.get('user_operation_id')),
                                     archive_filename)
        path_new = arc_converter.make_archive(dict_of_files['arc'])
        if isinstance(path_new, str):
            el_path_new = path_new.split('/')
            file_new = el_path_new[-1]
            return render_template('result.html', path=path_new, new_filename=file_new, title='Download')
    for errors in form.errors.values():
        for error in errors:
            flash(error, category='danger')
    return render_template('convert-arc.html', form=form, title='Archive Convert')


@app.route('/download/<path:file_path>', methods=['GET', 'POST'])
def download(file_path):
    try:
        if 'files' in file_path and session.get('user_operation_id') in file_path:
            splited = file_path.split('/')
            filename = splited[-1]
            path = '/'.join(splited[:-1])
            return send_from_directory(path, filename, as_attachment=True)
        return redirect(url_for('index'))
    except Exception as e:
        flash('Sorry, an unknown error occurred while getting the link to download the file.'
              ' Please try again later', category='danger')
        return redirect(url_for('index'))


@app.route('/picture-convert', methods=['GET', 'POST'])
def convert_picture():
    form = PictureForm()
    if form.validate_on_submit():
        check_operation_id()
        operation_id = session.get('user_operation_id')
        path_to_folder = create_folder(operation_id)
        filename = save_file(form.file.data.filename, path_to_folder, form.file.data)
        if filename is None:
            return redirect(url_for('index'))
        converter = PictureConverter(path_to_folder, filename)
        res = converter.convert(form.file_format.data)
        path = res['new_file_path'] if isinstance(error_converting(res), dict) else 'error'
        if path == 'error':
            return redirect(url_for('index'))
        new_file = path.split('/')[-1]
        return render_template('result.html', path=path, new_filename=new_file, title='Download')
    for errors in form.errors.values():
        for error in errors:
            flash(error, category='danger')
    return render_template('convert.html', form=form, title='Convert Image')


@app.route('/audio-convert', methods=['GET', 'POST'])
def convert_audio():
    form = AudioForm()
    if form.validate_on_submit():
        check_operation_id()
        operation_id = session.get('user_operation_id')
        path_to_folder = create_folder(operation_id)
        filename = save_file(form.file.data.filename, path_to_folder, form.file.data)
        if filename is None:
            return redirect(url_for('index'))
        converter = AudioConverter(path_to_folder, filename)
        res = converter.convert(form.file_format.data)
        path = res['new_file_path'] if isinstance(error_converting(res), dict) else 'error'
        if path == 'error':
            return redirect(url_for('index'))
        new_file = path.split('/')[-1]
        return render_template('result.html', path=path, new_filename=new_file, title='Download')
    for errors in form.errors.values():
        for error in errors:
            flash(error, category='danger')
    return render_template('convert.html', form=form, title='Convert Audio')


@app.route('/video-convert', methods=['GET', 'POST'])
def convert_video():
    form = VideoForm()
    if form.validate_on_submit():
        check_operation_id()
        operation_id = session.get('user_operation_id')
        path_to_folder = create_folder(operation_id)
        filename = save_file(form.file.data.filename, path_to_folder, form.file.data)
        if filename is None:
            return redirect(url_for('index'))
        converter = VideoConverter(path_to_folder, filename)
        res = converter.convert(form.file_format.data)
        path = res['new_file_path'] if isinstance(error_converting(res), dict) else 'error'
        if path == 'error':
            return redirect(url_for('index'))
        new_file = path.split('/')[-1]
        return render_template('result.html', path=path, new_filename=new_file, title='Download')
    for errors in form.errors.values():
        for error in errors:
            flash(error, category='danger')
    return render_template('convert.html', form=form, title='Convert video')


def check_operation_id():
    session['user_operation_id'] = uuid.uuid4().hex if session.get('user_operation_id') is None \
        else session.get('user_operation_id')


def error_converting(result):
    if not isinstance(result, dict):
        flash('An error occurred while converting the file.'
              ' It is possible that you have uploaded a broken file.'
              ' If the file is working, then try changing the format', category='danger')
        return None
    return result


def save_file(filename, path, file_data):
    try:
        filename = secure_filename(filename)
        file_data.save(os.path.join(path, filename))
        return filename
    except Exception as e:
        flash('Sorry, an unknown error occurred. Please try again later', category='danger')


if __name__ == '__main__':
    app.run(port=8080, debug=True)

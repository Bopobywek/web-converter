import os
import shutil

USER_FILES_DIRCTORY = 'files/'


def create_folder(name):
    if os.path.exists(os.path.join(USER_FILES_DIRCTORY, name)):
        delete_folder(name)
    os.mkdir(os.path.join(USER_FILES_DIRCTORY, name))
    return os.path.join(USER_FILES_DIRCTORY, name)


def delete_folder(name):
    shutil.rmtree(os.path.join(USER_FILES_DIRCTORY, name))


def delete_user_file():
    pass


def validate_file(path, name):
    if os.path.isdir(path):
        directory = os.listdir(path)
        return name in directory


def save_archive(path, filename, data):
    data.save(os.path.join(path, filename))
    os.mkdir(os.path.join(path, 'content'))


def save_file():
    pass

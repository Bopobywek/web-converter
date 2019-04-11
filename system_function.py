import os
import shutil
from convert_functions import VIDEO_SUPPORTED_FORMATS, AUDIO_SUPPORTED_FORMATS, PICTURE_SUPPORTED_FORMATS
from pathlib import Path

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


def get_file_type(file):
    suf = Path(file).suffix[1:].upper()
    if suf in AUDIO_SUPPORTED_FORMATS:
        return AUDIO_SUPPORTED_FORMATS
    elif suf in PICTURE_SUPPORTED_FORMATS:
        return PICTURE_SUPPORTED_FORMATS
    elif suf in VIDEO_SUPPORTED_FORMATS:
        return VIDEO_SUPPORTED_FORMATS


def save_archive(path, filename, data):
    data.save(os.path.join(path, filename))
    os.mkdir(os.path.join(path, 'content'))


def save_file():
    pass

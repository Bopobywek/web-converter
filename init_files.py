import os


def create_files():
    if not os.path.exists('files'):
        os.mkdir('files')

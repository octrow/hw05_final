import os
import sys

import requests
from django.core.management import execute_from_command_line

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yatube.settings')


def download_bootstrap():
    CSS_FILE_NAME = 'bootstrap.min.css'
    CSS_FILE_URL = ('https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1'
                    + '/dist/css/bootstrap.min.css')
    CSS_FILE_DIR = 'static/css'
    JS_FILE_NAME = 'bootstrap.bundle.min.js'
    JS_FILE_URL = (
        'https://getbootstrap.com/docs/5.3/dist/js/bootstrap.bundle.min.js'
    )
    JS_FILE_DIR = 'static/js'
    POPPER_FILE_NAME = 'popper.min.js'
    POPPER_FILE_URL = (
        'https://unpkg.com/@popperjs/core@2.11.6/dist/umd/popper.min.js'
    )
    POPPER_FILE_DIR = 'static/js'

    if not os.path.exists(CSS_FILE_DIR):
        os.makedirs(CSS_FILE_DIR)

    if not os.path.isfile(os.path.join(CSS_FILE_DIR, CSS_FILE_NAME)):
        response = requests.get(CSS_FILE_URL)
        response.raise_for_status()
        with open(os.path.join(CSS_FILE_DIR, CSS_FILE_NAME), 'wb') as f:
            f.write(response.content)
    print('Проверка и загрузка Bootstrap CSS file')

    if not os.path.exists(JS_FILE_DIR):
        os.makedirs(JS_FILE_DIR)
    if not os.path.isfile(os.path.join(JS_FILE_DIR, JS_FILE_NAME)):
        response = requests.get(JS_FILE_URL)
        response.raise_for_status()
        with open(os.path.join(JS_FILE_DIR, JS_FILE_NAME), 'wb') as f:
            f.write(response.content)
    print('Проверка и загрузка Bootstrap JS file')

    if not os.path.exists(POPPER_FILE_DIR):
        os.makedirs(POPPER_FILE_DIR)
    if not os.path.isfile(os.path.join(POPPER_FILE_DIR, POPPER_FILE_NAME)):
        response = requests.get(POPPER_FILE_URL)
        response.raise_for_status()
        with open(os.path.join(POPPER_FILE_DIR, POPPER_FILE_NAME), 'wb') as f:
            f.write(response.content)
    print('Проверка и загрузка Popper JS')


def main():
    try:
        execute_from_command_line(sys.argv)
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc


if __name__ == '__main__':
    download_bootstrap()
    main()

import math
import logging
import requests
import os
import shutil

log = logging.getLogger(__name__)


def create_temp_folder(folder):
    if os.path.exists(folder) and not os.path.isdir(folder):
        print('Folder name already used in file. Creating as temp folder')
        os.remove(folder)
        os.mkdir(folder)
    elif os.path.exists(folder) and os.path.isdir(folder):
        print('Folder already exists. Cleaning temp folder')
        shutil.rmtree(folder)
        os.mkdir(folder)
    elif not os.path.exists(folder):
        print('Creating temp folder')
        os.mkdir(folder)


def download_to_file(url, filename):
    response = requests.get(url)

    if response.ok:
        with open(filename, 'wb') as f:
            f.write(response.content)

        return response
    else:
        return response


def to_float(value):
    try:
        number = float(value)
        return None if math.isnan(number) else number
    except Exception as e:
        log.warn(e)
        return None


def to_int(value):
    try:
        number = int(value)
        return None if math.isnan(number) else number
    except Exception as e:
        log.warn(e)
        return None

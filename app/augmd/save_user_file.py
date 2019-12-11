from flask import current_app
from flask_login import current_user
import os

def save_user_file(data, name, ext, save=True):
    if not os.path.exists(current_app.instance_path):
        os.mkdir(current_app.instance_path)
    if not os.path.exists(os.path.join(current_app.instance_path, 'files')):
        os.mkdir(os.path.join(current_app.instance_path, 'files'))
    if not os.path.exists(os.path.join(current_app.instance_path, 'files', current_user.username)):
        os.mkdir(os.path.join(current_app.instance_path, 'files', current_user.username))
    filename = os.path.join(current_app.instance_path, 'files', current_user.username, f'{name}.{ext}')
    if data and save:
        data.save(filename)
    return filename
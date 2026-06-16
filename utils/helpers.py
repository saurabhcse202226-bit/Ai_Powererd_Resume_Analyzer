import os
import uuid
from config import Config


def allowed_file(filename):
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in Config.ALLOWED_EXTENSIONS


def save_uploaded_file(file):
    """Save file and return (saved_filename, original_name, file_size)"""
    original_name = file.filename
    ext = original_name.rsplit('.', 1)[1].lower() if '.' in original_name else 'txt'

    # use uuid so filenames don't collide
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(Config.UPLOAD_FOLDER, unique_name)

    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    file.save(filepath)

    file_size = os.path.getsize(filepath)
    return unique_name, original_name, file_size, filepath


def delete_file(filename):
    filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False

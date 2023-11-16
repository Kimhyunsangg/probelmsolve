from flask import request
import os

UPLOAD_FOLDER = 'data'

def upload_file():
    if 'file' not in request.files:
        return '파일을 찾을 수 없습니다.'

    file = request.files['file']
    
    if file.filename == '':
        return '파일 이름이 없습니다.'

    if file:
        if not os.path.isdir(UPLOAD_FOLDER):
            os.mkdir(UPLOAD_FOLDER)
        file.save(os.path.join(UPLOAD_FOLDER, file.filename))
        return '파일 업로드 완료: ' + file.filename

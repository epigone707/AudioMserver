from fileinput import filename
import os
from django.shortcuts import render
from flask import Flask, jsonify, render_template, request, redirect, url_for, abort, send_from_directory
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
import audio_metadata

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# db.init_app(app)

app.config["ALLOWED_EXTENSIONS"] = ['wav', 'mp3']

app.config["UPLOAD_PATH"] = 'uploads/'


class Metadata(db.Model):
    filename = db.Column(db.String, unique=True,
                         nullable=False, primary_key=True)
    filesize = db.Column(db.Integer)
    duration = db.Column(db.Integer)
    album = db.Column(db.String)
    artist = db.Column(db.String)
    title = db.Column(db.String)


@app.route('/')
def index():
    return render_template('index.html')


def validate_audio(uploaded_file):
    # TODO

    return True


def validate_audio_fname(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


def get_sec(duration):
    """Get seconds from time."""
    # count = 0
    # for c in time_str:
    #     if c == ':':
    #         count += 1
    # if count == 2:
    #     h, m, s = time_str.split(':')
    #     return int(h) * 3600 + int(m) * 60 + int(s)
    # elif count == 1:
    #     m, s = time_str.split(':')
    #     return int(m) * 60 + int(s)
    # else:
    #     print(f"invalid duration string: {time_str}")
    #     return 0
    return int(duration)


@app.route('/post', methods=['POST'])
def upload_files():
    print("upload_files")
    # uploaded_file = request.files['file']
    # requestJson = request.get_json(force=True)
    # print("requestJson:",requestJson)
    # print("request:", request)
    # print("request.headers:",request.headers)
    # print("request.files:",request.files)
    # file = request.files['file']
    # print(file.filename)
    # print("request.args:",request.args)
    # print("request.form:",request.form)
    # print("request.get_data():",request.get_data())
    mimetype = request.mimetype
    filename = ""
    if mimetype == 'application/x-www-form-urlencoded':
        print("content-type: application/x-www-form-urlencoded")
        filename = "test.wav"
        with open(os.path.join(app.config['UPLOAD_PATH'], filename), 'wb') as f:
            f.write(request.get_data())
        metadata = audio_metadata.load(
            os.path.join(app.config['UPLOAD_PATH'], filename))
        new_title = metadata["tags"]["title"][0]
        new_filename = new_title+".wav"
        os.rename(os.path.join(app.config['UPLOAD_PATH'], filename), os.path.join(app.config['UPLOAD_PATH'], new_filename))
        upload = Metadata(filename=new_filename,
                          filesize=metadata['filesize'],
                          duration=get_sec(metadata['streaminfo']['duration']),
                          album=metadata["tags"]["album"][0],
                          artist=metadata["tags"]["artist"][0],
                          title=new_title,
                          )
        db.session.add(upload)
        db.session.commit()
        return jsonify(
            status="success",
            response=f"Your file is renamed as {new_filename}."
        )
    elif mimetype == 'multipart/form-data':
        print("content-type: multipart/form-data")
        uploaded_file = request.files['file']
        filename = secure_filename(uploaded_file.filename)
        if filename == '':
            return "Empty audio filename", 400
        if not validate_audio_fname(filename):
            return "Invalid audio filename", 400
        if validate_audio(uploaded_file) == False:
            return "Invalid audio file", 400

        uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
        metadata = audio_metadata.load(
            os.path.join(app.config['UPLOAD_PATH'], filename))
        print(metadata)

        upload = Metadata(filename=filename,
                          filesize=metadata['filesize'],
                          duration=get_sec(metadata['streaminfo']['duration']),
                          album=metadata["tags"]["album"][0],
                          artist=metadata["tags"]["artist"][0],
                          title=metadata["tags"]["title"][0],
                          )
        db.session.add(upload)
        db.session.commit()

        return jsonify(
            status="success",
            response=f"Your file is uploaded as {filename}."
        )
    else:
        return "Invalid content type", 400


@app.route('/download', methods=['GET'])
def download():
    args_dict = request.args.to_dict()
    print(args_dict)

    file_name = args_dict.get("name")
    with open(os.path.join(app.config['UPLOAD_PATH'], file_name), 'rb') as fd:
        contents = fd.read()
    return jsonify(
        filename=file_name,
        found=True,
        contents=str(contents)
    )


@app.route('/info', methods=['GET'])
def meta_info():
    args_dict = request.args.to_dict()
    print(args_dict)

    file_name = args_dict.get("name")
    meta_data = db.get_or_404(Metadata, file_name)
    d = {}
    for column in meta_data.__table__.columns:
        d[column.name] = str(getattr(meta_data, column.name))
    return jsonify(
        filename=file_name,
        found=True,
        metadata=d
    )


@app.route('/list', methods=['GET'])
def filtered_list():
    args_dict = request.args.to_dict()
    print(args_dict)

    if "maxduration" in args_dict:
        maxduration = int(args_dict.get("maxduration"))
        print(maxduration)
        rows = db.session.execute(db.select(['*']).filter(
            Metadata.duration <= maxduration))
        res = []
        for row in rows:
            print(row)
            print(type(row))
            res.append(dict(row._mapping))
        return jsonify(
            found=(len(res) > 0),
            results=res
        )
    else:
        return jsonify(
            found=False,
            results="Invalid query paramenter."
        )


if __name__ == '__main__':
    # app.run(port=80)
    with app.app_context():
        # create the tables only when they don't exist and would not change the tables created before.
        db.create_all()
    app.run()

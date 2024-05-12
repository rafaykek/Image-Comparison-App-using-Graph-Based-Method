from flask import Flask, flash, request, redirect, url_for, render_template
import os
from werkzeug.utils import secure_filename
from Functions import checkSimilarity , displayGraph
from flask import jsonify

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join('project', 'static', 'uploads')
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    uploaded_files = [request.files['file1'], request.files['file2']]

    filenames = []
    for file in uploaded_files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            filenames.append(filename)
        else:
            flash('Allowed image types are - png, jpg, jpeg, gif')
            return redirect(request.url)

    flash('Images successfully uploaded and displayed below')
    return ",".join(filenames)  # Sending comma-separated filenames


@app.route('/check_similarity')
def check_similarity():
    retList = checkSimilarity()
    return jsonify(retList)

@app.route('/display_graph')
def display_graph():
    graph_folder = 'project/static/graphs'
    filenames = os.listdir(graph_folder)
    return jsonify(filenames)



if __name__ == "__main__":
    app.run(debug=True)

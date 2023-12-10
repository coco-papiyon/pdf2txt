from flask import Flask, render_template, request, redirect
import glob
import os
import json
import convert
import requests

app = Flask(__name__, static_folder="image", static_url_path='/image')

JSON_DIR = 'json'
IMAGE_DIR = 'image'
PDF_DIR = 'pdf'

@app.route('/')
def index():
    print('start: index')

    pages = []
    for file in glob.glob(os.path.join(JSON_DIR, '*.json')):
        file = file.replace('\\', '/')
        file = os.path.splitext(os.path.basename(file))[0]
        pages.append(file)

    return render_template('index.html', pages=pages) 

@app.route('/json/<file>')
def show_file(file):
    print('start: show_file')
    
    name = file
    file = os.path.join(JSON_DIR, file + ".json")
    data = None
    with open(file, 'r') as f:
        data = json.load(f)

    return render_template('json.html', data=data, name=name) 

@app.route('/upload', methods=["GET", "POST"])
def upload():
    print('start: upload')

    if request.method == "GET":
        return redirect('/')

    os.makedirs(PDF_DIR, exist_ok=True)

    url = request.form["url"]
    filename = request.form["name"]
    if url != '':
        filepath = ''
        if filename != '':
            filepath = os.path.join(PDF_DIR, filename + '.pdf')
        else:
            filepath = os.path.basename(url)
            filepath = filepath.split('?')[0]
            if os.path.splitext(filepath)[1] == 'pdf':
                filepath = os.path.join(PDF_DIR, filepath + '.pdf')
            filename = os.path.splitext(os.path.basename(filepath))[0]

        print('get url: ' + url + " to " + filepath)

        data = requests.get(url).content
        with open(filepath ,mode='wb') as f:
            f.write(data)

        print('convert: ' + filepath)
        convert.convert(filepath)

        filename = filename.replace(' ', '_')
        return redirect('/json/' + filename)

    file = request.files['file']
    if file.filename != '':
        filename = file.filename
        print('upload: ' + filename)

        filepath = os.path.join(PDF_DIR, filename)
        file.save(filepath)
            
        print('convert: ' + filepath)
        convert.convert(filepath)

        filename = os.path.splitext(os.path.basename(filename))[0]
        filename = filename.replace(' ', '_')
        return redirect('/json/' + filename)
    
    return redirect('/')

if __name__ == '__main__':
    app.run()
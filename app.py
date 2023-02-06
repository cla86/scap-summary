from flask import Flask, send_from_directory
from flask import request, redirect, jsonify
from werkzeug.utils import secure_filename
from bs4 import BeautifulSoup
import os
import re

UPLOAD_FOLDER = 'reports'

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = set(['html', 'htm'])

@app.route('/')
def hello_world():
    return 'Hello, Docker!'

#@app.route('/reports/<host:host>')
#def reports_host(host):
#    return send_from_directory('reports', host, '.html')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def rules_number(a):
    x = re.findall('[0-9]+', a)
    return int(x[0])

def compliance_summary(summary):
    final = rules_number(summary)
    #final = final.text.rstrip()
    return final

def compliance_report(content):
    soup = BeautifulSoup(content, "html.parser")
    scoring = soup.find("div", title="Displays proportion of passed/fixed, failed/error, and other rules (in that order). There were $not_ignored_rules_count rules taken into account.")
    success = compliance_summary(scoring.find("div", class_="progress-bar progress-bar-success").text.rstrip())
    danger = compliance_summary(scoring.find("div", class_="progress-bar progress-bar-danger").text.rstrip())
    warning = compliance_summary(scoring.find("div", class_="progress-bar progress-bar-warning").text.rstrip())
    severity_failed = soup.find("div", title="Displays proportion of high, medium, low, and other severity failed rules (in that order). There were 154 total failed rules.")

    #scoring = soup.find_all("div", class_="progress-bar")
    #ret = {'success': succes
    #       , 'danger': danger, 'warning': warning}
    ret = {'passed': success,
            'failed': danger,
            'warning': warning, 
            'severity': str(severity_failed) }
    return ret

@app.route('/reports/<path:path>', methods=['POST', 'GET'])
def report(path):
    if request.method == 'GET':
        print('reports/' + path)
        #try:
        with open('reports/' + path) as f:
            content = f.read()
            resp = jsonify({'message': compliance_report(content)})
            #resp = compliance_report(content)
            resp.status_code = 200
            return resp
        #except:
        #    resp = jsonify({'message' : 'No report'})
        #    resp.status_code = 400
        #    return resp
        #return send_from_directory('reports', path)
    elif request.method == 'POST':
        print(request)
        if 'file' not in request.files:
            resp = jsonify({'message' : 'No file part in the request'})
            resp.status_code = 400
            return resp
        file = request.files['file']
        if file.filename == '':
            resp = jsonify({'message' : 'No file selected for uploading'})
            resp.status_code = 400
            return resp
        if file and allowed_file(file.filename):
            filename = secure_filename(path)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            resp = jsonify({'message' : 'File successfully uploaded'})
            resp.status_code = 201
            return resp
        else:
             resp = jsonify({'message' : 'Allowed file types are html, htm, pdf'})
             resp.status_code = 400
             return resp


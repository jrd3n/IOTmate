from flask import Flask, render_template, request, jsonify, url_for,redirect, send_file
from werkzeug.utils import secure_filename
import json
import os

app = Flask(__name__, static_url_path='/static')

def write_test_json_file(smo, data):
    filepath = f'data/{smo}/test_data.json'
    with open(filepath, 'w') as file:
        json.dump(data, file)

def read_file(folder_path,file_name):
    job_file_path = os.path.join(folder_path, file_name)
    if os.path.exists(job_file_path):
        with open(job_file_path, 'r') as file:
            json_data = json.load(file)

    return json_data

def read_test_json_file(smo):
    filepath = f'data/{smo}/test_data.json'
    
    try:
        with open(filepath, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        print(f"No test_data.json file found in the folder data/{smo}")

        empty_dict = {"Empty": {
                                "title": "",
                                "requirments": "",
                                "operator": "",
                                "date": "",
                                "status": "",
                                "method": "",
                                "criteria": "",
                                "conclusion": "",
                                "method-comment": "",
                                "criteria-comment": ""
                            }
                                }
        data = empty_dict  # Directly return the empty dictionary
    
    return data

def read_job_json_file(smo):
    job_file_path = f'data/{smo}/job.json'
    
    if os.path.exists(job_file_path):
        with open(job_file_path, 'r') as file:
            job_data = json.load(file)
            return job_data
    else:
        return {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/all_jobs', methods=['GET'])
def get_all_jobs():
    all_jobs = []
    data_dir = 'data'

    for folder in os.listdir(data_dir):
        folder_path = os.path.join(data_dir, folder)

        if os.path.isdir(folder_path):
            job_data = read_file(folder_path, 'job.json')
            all_jobs.append(job_data)

    return jsonify(all_jobs)

@app.route('/upload', methods=['POST'])
def handle_upload():

    smo = request.form.get('smo')
    test = request.form.get('test')

    print('{smo} and test {test}'.format(smo=smo, test=test))

    if test != "":
        upload_folder = f'data/{smo}/{test}/'
    else:
        upload_folder = f'data/{smo}/'

    print(upload_folder)
   
    app.config['UPLOAD_FOLDER'] = upload_folder

    def save_file(file, upload_folder):
    # Save the uploaded file
        filename = secure_filename(file.filename)

        # Make sure the upload folder exists
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        file.save(os.path.join(upload_folder, filename))

        return os.path.join(upload_folder, filename)

    if 'file' in request.files:
        print("OTHER FILE")
        other_file = request.files['file']
        if other_file:
            save_file(other_file, upload_folder)

    next_url = request.form.get('next') or url_for('default_route')
    return redirect(next_url)

@app.route('/<smo>/<test>', methods=['GET', 'POST'])
def test_form(smo, test):

    test_data = read_test_json_file(smo)
    job_info = read_job_json_file(smo)

    default_test_data = {
        "title": "",
        "operator": "",
        "date": "",
        "status": "",
        "method": "",
        "criteria": "",
        "conclusion": ""
    }

    if request.method == 'POST':

        # Handle form submission
        for field in request.form:
            submitted_value = request.form.get(field)
            if test_data[test].get(field) != submitted_value:
                test_data[test][field] = submitted_value

        write_test_json_file(smo, test_data)
        return redirect(url_for('test_form', smo=smo, test=test))
    
    # After line where app.config['UPLOAD_FOLDER'] is set
    app.config['UPLOAD_FOLDER'] = f'data/{smo}/{test}/'
    
    # List all files in upload directory
    files = os.listdir(app.config['UPLOAD_FOLDER']) if os.path.exists(app.config['UPLOAD_FOLDER']) else []

    # Update default_test_data with the actual data from the JSON file
    actual_test_data = test_data.get(test, {})
    test_data_merged = {**default_test_data, **actual_test_data}

    # Include `files` in the `render_template` method
    return render_template('test_form.html', test_data=test_data_merged, smo=smo, test=test, job_info=job_info, files=files)

@app.route('/<smo>')
def test_toc(smo):
    tests = read_test_json_file(smo)
    #print(tests)

    # After line where app.config['UPLOAD_FOLDER'] is set
    app.config['UPLOAD_FOLDER'] = f'data/{smo}/'
    
    # List all files in upload directory
    # List all files in upload directory
    if os.path.exists(app.config['UPLOAD_FOLDER']):
        files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], f))]
    else:
        files = []

    job_info = read_job_json_file(smo)
    return render_template('test_toc.html', tests=tests, smo=smo, job_info=job_info, files=files)

@app.route('/<smo>/<test>/download/<filename>')
def download_file_from_test(filename,smo,test):

    filepath = f'data/{smo}/{test}/{filename}'

    return send_file(filepath, as_attachment=True) 

@app.route('/<smo>/download/<filename>')
def download_file_from_job(filename,smo):

    filepath = f'data/{smo}/{filename}'

    return send_file(filepath, as_attachment=True)

@app.route('/<smo>/data', methods=['GET', 'POST'])
def data(smo):
    job_file_path = f'data/{smo}/job.json'

    if request.method == 'GET':
        if os.path.exists(job_file_path):
            with open(job_file_path, 'r') as file:
                job_data = json.load(file)
                return jsonify(job_data)
        else:
            return jsonify({})
        
    elif request.method == 'POST':

        new_data = request.json

        smo_path = f"data/{smo}"
    
        if not os.path.exists(smo_path):
            os.makedirs(smo_path)
            
            job_data = {
                "job_name": "",
                "client": "",
                "location": "",
                "start_date": "",
                "end_date": "",
                "description": ""
            }

            with open(f"{smo_path}/job.json", 'w') as file:
                json.dump(job_data, file)

        with open(job_file_path, 'w') as file:
            json.dump(new_data, file)
        return jsonify({'success': True})

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True , port=5001)
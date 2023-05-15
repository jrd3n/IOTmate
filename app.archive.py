from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
from werkzeug.utils import secure_filename
import json
import os

app = Flask(__name__, static_url_path='/static')

def write_test_json_file(smo, data):
    filepath = f'data/{smo}/test_data.json'
    with open(filepath, 'w') as file:
        json.dump(data, file)

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

# def get_smos():
#     data_dir = 'data'
#     smos = [name for name in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, name))]
#     return smos

# def get_client(smo):
#     job_file_path = f'data/{smo}/job.json'
    
#     if os.path.exists(job_file_path):
#         with open(job_file_path, 'r') as file:
#             job_data = json.load(file)
#             return job_data.get('client', 'N/A')
#     else:
#         return 'N/A'

def create_smo_directory(smo):
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

# @app.route('/create_smo', methods=['POST'])
# def create_smo_form():
#     smo = request.form['smo']
#     create_smo_directory(smo)

#     return redirect(url_for('index'))

#### ok below

# @app.route('/<smo>')
# def smo_table(smo):
#     tests = read_test_json_file(smo)
#     job_data = read_job_json_file(smo)
#     return render_template('test_toc.html', smo=smo, tests=tests, job_data=job_data)

@app.route('/<smo>')
def test_toc(smo):
    tests = read_test_json_file(smo)
    job_info = read_job_json_file(smo)
    return render_template('test_toc.html', tests=tests, smo=smo, job_info=job_info)

# @app.route('/<smo>/json')
# def get_test_json(smo):
#     data = read_test_json_file(smo)
#     return jsonify(data)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico')

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

                # Check if there is a file uploaded
        if 'photo' in request.files:
            photo = request.files['photo']
            if photo and allowed_file(photo.filename):
                filename = secure_filename(photo.filename)

                app.config['UPLOAD_FOLDER'] = f'data/{smo}/{test}/'

                # Make sure the upload folder exists
                if not os.path.exists(app.config['UPLOAD_FOLDER']):
                    os.makedirs(app.config['UPLOAD_FOLDER'])

                photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                test_data[test]['photo_path'] = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # Handle form submission
        for field in request.form:
            submitted_value = request.form.get(field)
            if test_data[test].get(field) != submitted_value:
                test_data[test][field] = submitted_value

        write_test_json_file(smo, test_data)
        return redirect(url_for('test_form', smo=smo, test=test))

    # Update default_test_data with the actual data from the JSON file
    actual_test_data = test_data.get(test, {})
    test_data_merged = {**default_test_data, **actual_test_data}

    return render_template('test_form.html', test_data=test_data_merged, smo=smo, test=test, job_info=job_info)
  
@app.route('/')
def index():
    print("Load index")
    return render_template('index.html')

@app.route('/all_jobs', methods=['GET'])
def get_all_jobs():
    all_jobs = []
    data_dir = 'data'

    for folder in os.listdir(data_dir):
        folder_path = os.path.join(data_dir, folder)
        if os.path.isdir(folder_path):
            job_file_path = os.path.join(folder_path, 'job.json')
            if os.path.exists(job_file_path):
                with open(job_file_path, 'r') as file:
                    job_data = json.load(file)
                    all_jobs.append(job_data)

    return jsonify(all_jobs)

@app.route('/create_smo', methods=['POST'])
def create_smo_form():
    smo = request.form['job_number']
    create_smo_directory(smo)
    return redirect(url_for('index'))



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8090, debug=True, threaded=False)
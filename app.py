from flask import Flask, render_template, request, jsonify, url_for,redirect, send_file
from werkzeug.utils import secure_filename
import openpyxl
import pandas as pd
import json
import os

app = Flask(__name__, static_url_path='/static')

def write_json_to_excel(folder_path,file_name,json):

    full_file_path = os.path.join(folder_path, file_name)
    if os.path.exists(full_file_path):
        with open(full_file_path, 'r') as file:
            json_data = json.load(file)

def read_json_from_excel(folder_path,file_name):

    full_file_path = os.path.join(folder_path, file_name)
    if os.path.exists(full_file_path):

        # Load the Excel file
        df = pd.read_excel(full_file_path)

        # Convert the DataFrame back to a dictionary
        data = df.to_dict(orient='records')

        #print(data)

        return data

    else:
        print("ERROR NO FILE NAMED {file_name} in folder {folder_path}".format(file_name=file_name,folder_path=folder_path))
        pass

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
            job_data = read_json_from_excel(folder_path, 'job_information.xlsx')
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

    test_number = test

    folder_path = f'data/{smo}/'

    all_test_data = read_json_from_excel(folder_path,file_name="test_data.xlsx")
    job_data = read_json_from_excel(folder_path, 'job_information.xlsx')

    # print(all_test_data)

    filtered_test = [test for test in all_test_data if test["Number"].strip() == test_number]

    if filtered_test:  # check if the filtered_test list is not empty
        filtered_test = filtered_test[0]  # Get the first (and should be the only) item in the list
    else:
        print(f"No test with Number: {test_number} found.")

    #print(filtered_test)

    if request.method == 'POST':

        # Handle form submission
        for field in request.form:
            submitted_value = request.form.get(field)
            if test_data[test_number].get(field) != submitted_value:
                test_data[test_number][field] = submitted_value

        write_test_json_file(smo, test_data)
        return redirect(url_for('test_form', smo=smo, test=test_number))
    
    # After line where app.config['UPLOAD_FOLDER'] is set
    app.config['UPLOAD_FOLDER'] = f'data/{smo}/{test_number}/'
    
    # List all files in upload directory
    files = os.listdir(app.config['UPLOAD_FOLDER']) if os.path.exists(app.config['UPLOAD_FOLDER']) else []

    # Include `files` in the `render_template` method
    return render_template('test_form.html', test_data=filtered_test, smo=smo, job_info=job_data, files=files)

@app.route('/<smo>')
def test_toc(smo):
    folder_path = f'data/{smo}/'
    tests = read_json_from_excel(folder_path=folder_path,file_name="test_data.xlsx")

    # After line where app.config['UPLOAD_FOLDER'] is set
    app.config['UPLOAD_FOLDER'] = f'data/{smo}/'
    
    # List all files in upload directory
    if os.path.exists(app.config['UPLOAD_FOLDER']):
        files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], f))]
    else:
        files = []

    job_info = read_json_from_excel(folder_path=folder_path,file_name="job_information.xlsx")

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